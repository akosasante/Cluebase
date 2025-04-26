#!/usr/bin/env python
# -*- coding: utf-8 -*-

import aiohttp
import asyncio
from pathlib import Path

class SeasonDownloader:
    def __init__(self, url, archive_folder="j-archive"):
        self.url = url
        self.archive_folder = Path(archive_folder)
        self.season_file = self.archive_folder / "seasons" / "seasons.html"

    def create_archive_dir(self):
        if not self.archive_folder.exists():
            print(f"Making directory: {self.archive_folder}")
            self.archive_folder.mkdir(parents=True)

    async def download_season_list(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                if response.status == 200:
                    content = await response.text()
                    self.season_file.write_text(content)
                    print(f"Downloaded season list to {self.season_file}")
                else:
                    print(f"Failed to download season list: HTTP {response.status}")

    async def run(self):
        self.create_archive_dir()
        await self.download_season_list()

async def main():
    downloader = SeasonDownloader(url='https://www.j-archive.com/listseasons.php')
    await downloader.run()

if __name__ == "__main__":
    asyncio.run(main())