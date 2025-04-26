#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import aiohttp
import os
from pathlib import Path
import json
from tqdm import tqdm
import multiprocessing

class Downloader:
    def __init__(self, base_url, start_page=1, max_concurrent=None, archive_folder="j-archive"):
        self.base_url = base_url
        self.start_page = start_page
        self.archive_folder = Path(archive_folder)
        self.games_folder = self.archive_folder / "games"
        # pathlib module lets you use `/` to join Path + string
        self.progress_file = self.archive_folder / "games_progress.json"

        # Use CPU count for max_concurrent if not specified
        if max_concurrent is None:
            self.max_concurrent = multiprocessing.cpu_count() * 2
        else:
            self.max_concurrent = max_concurrent

        print(f'Using {self.max_concurrent} concurrent connections')

        # Rate limiting
        self.SECONDS_BETWEEN_REQUESTS = 0.5
        self.ERROR_MSG = "ERROR: No game"

    def create_archive_dir(self):
        if not self.archive_folder.exists():
            print(f"Making directory: {self.archive_folder}")
            self.archive_folder.mkdir(parents=True)
        if not self.games_folder.exists():
            print(f"Making directory: {self.games_folder}")
            self.games_folder.mkdir()

    def load_progress(self):
        if self.progress_file.exists():
            return set(json.loads(self.progress_file.read_text()))
        return set()

    def save_progress(self, completed):
        self.progress_file.write_text(json.dumps(list(completed)))

    async def download_page(self, session, page):
        url = f'{self.base_url}?game_id={page}'
        filename = self.games_folder / f"{page}.html"

        if filename.exists():
            return page, True, "already_exists"

        try:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.text()
                    if self.ERROR_MSG in content:
                        return page, False, "end_reached"

                    filename.write_text(content)
                    await asyncio.sleep(self.SECONDS_BETWEEN_REQUESTS)
                    return page, True, "downloaded"
                else:
                    return page, False, f"http_{response.status}"
        except Exception as e:
            return page, False, f"error_{str(e)}"

    async def run(self):
        self.create_archive_dir()
        completed = self.load_progress()

        async with aiohttp.ClientSession() as session:
            page = self.start_page
            end_reached = False
            # Progress Bar
            pbar = tqdm(desc="Downloading pages", unit="page")

            while not end_reached:
                tasks = []
                # Create batch of tasks
                for _ in range(self.max_concurrent):
                    if str(page) not in completed:
                        tasks.append(asyncio.create_task(self.download_page(session, page)))
                    page += 1

                if not tasks:
                    break

                # Wait for batch to complete
                results = await asyncio.gather(*tasks)

                for page_num, success, status in results:
                    if status == "end_reached":
                        end_reached = True
                        break
                    elif status == "downloaded":
                        completed.add(str(page_num))
                        self.save_progress(completed)
                        pbar.update(1)
                        pbar.set_postfix({"status": "downloaded", "page": page_num})
                    elif status == "already_exists":
                        completed.add(str(page_num))
                        pbar.update(1)
                        pbar.set_postfix({"status": "existing", "page": page_num})
                    else:
                        pbar.set_postfix({"status": f"failed_{status}", "page": page_num})

            pbar.close()
            print("\nFinished downloading. Ready for parsing.")

async def main():
    downloader = Downloader(
        base_url='https://www.j-archive.com/showgame.php',
        start_page=1,
        max_concurrent=multiprocessing.cpu_count() * 2
    )
    await downloader.run()

if __name__ == "__main__":
    # By running this inside asyncio.run, we can use async/await syntax
    # It creates an event loop, runs the coroutine, and closes the loop
    asyncio.run(main())

# Created/Modified files during execution:
# - j-archive/games/*.html (one file per successfully downloaded page)
# - j-archive/games_progress.json (tracks completed downloads)