#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from pathlib import Path
import asyncio
import asyncpg
import argparse
import re
from datetime import datetime
from tqdm import tqdm
import traceback

class JeopardyParser:
    def __init__(self, db_config, archive_dir):
        self.db_config = db_config
        self.archive_dir = Path(archive_dir) / "games"
        self.pool = None

    async def init_db_pool(self):
        self.pool = await asyncpg.create_pool(**self.db_config)

    async def close(self):
        if self.pool:
            await self.pool.close()

    async def get_season_for_date(self, conn, air_date):
        """Get the season ID for a given air date."""
        season = await conn.fetchrow('''
            SELECT id 
            FROM seasons 
            WHERE start_date <= $1 AND end_date >= $1
        ''', air_date)

        if season:
            return season['id']
        else:
            # You might want to create a new season or handle this case differently
            return None

    async def get_contestants_by_player_ids(self, conn, contestant_player_ids, contestant_names):
        """Get a list of contestant IDs given their j-archive ids"""
        contestant_ids = []
        for name, player_id in zip(contestant_names, contestant_player_ids):
            # Upsert contestant if jarchive id is not already set or is set to the same value
            row = await conn.fetchrow(
                '''
                INSERT INTO contestants (name, jarchive_id)
                VALUES ($1, $2)
                ON CONFLICT (name) DO UPDATE
                SET jarchive_id = EXCLUDED.jarchive_id
                WHERE (contestants.jarchive_id IS NULL) OR (contestants.jarchive_id = EXCLUDED.jarchive_id)
                RETURNING id
                ''',
                name, player_id
            )
            if row:
                contestant_ids.append(row['id'])
            else:
                # Just grab contestant by id otherwise; most likely case is its a contestant who has played in multiple
                # tournaments and thus been archived under multiple player ids; we'll have to go back and fix that later
                row = await conn.fetchrow(
                    '''
                    INSERT INTO contestants (name, jarchive_id)
                    VALUES ($1, $2)
                    ON CONFLICT (name) DO UPDATE
                    SET jarchive_id = EXCLUDED.jarchive_id,
                        alternate_jarchive_ids = contestants.alternate_jarchive_ids || EXCLUDED.jarchive_id
                    WHERE contestants.jarchive_id IS NOT NULL 
                        AND contestants.jarchive_id != EXCLUDED.jarchive_id 
                        AND ((contestants.alternate_jarchive_ids IS NULL) OR ($2 != ANY(contestants.alternate_jarchive_ids)))
                    RETURNING id
                    ''',
                    name, player_id
                )
                if row:
                    contestant_ids.append(row['id'])
                else:
                    print(f"Failed to get contestant ID for {name} {player_id}; contestant_ids = {contestant_ids}")
        return contestant_ids

    def parse_final_scores(self, soup, contestant_ids):
        """Parse final scores and determine winner."""
        final_scores_section = soup.find('div', id='final_jeopardy_round')
        if not final_scores_section:
            return [None, None, None], [None, None, None], None

        # Get contestant nicknames and scores
        score_cells = final_scores_section.find_all('td', class_=re.compile(r'score_(positive|negative)'))
        all_scores = [float(cell.get_text().replace(',', '').replace('$', '')) for cell in score_cells]
        scores = all_scores[0:3]
        coryats = all_scores[3:6]

        # Pad with None if less than 3 scores somehow
        while len(scores) < 3:
            scores.append(float('-inf'))
        while len(coryats) < 3:
            coryats.append(float('-inf'))

        winner_idx = max(enumerate(scores), key=lambda x: x[1])[0]
        winner_id = contestant_ids[winner_idx]

        scores = [int(score) if score != float('-inf') else None for score in scores]
        coryats = [int(coryat) if coryat != float('-inf') else None for coryat in coryats]
        return scores, coryats, winner_id

    async def parse_game_file(self, file_path: Path, do_upsert: bool = False):
        """Parse a single game file and insert into database."""
        with open(file_path) as f:
            soup = BeautifulSoup(f, "lxml")

            async with self.pool.acquire() as conn:
                # Extract game metadata
                jarchive_id = int(re.search(r'(\d+)\.html', f.name).group(1))
                # eg title = 'J! Archive - Show #1148, aired 1989-09-06'
                # eg title = 'J! Archive - The Greatest of All Time game #3, aired 2020-01-08'
                # eg title = 'J! Archive - Super Jeopardy! show #10, aired 1990-08-18'
                # eg title = 'J! Archive - Trebek pilot #2, taped 1984-01-01'
                title = soup.title.get_text()
                episode_num = int(re.search(r'(?:Show|show|game|pilot) #(\d+)', title).group(1))
                air_date = datetime.strptime(title.split()[-1], '%Y-%m-%d').date()
                season_id = await self.get_season_for_date(conn, air_date)
                contestants_div = soup.find('div', id='contestants')
                contestant_links = contestants_div.find_all('a', href=re.compile(r'showplayer\.php\?player_id=\d+'))
                contestant_player_ids = [int(re.search(r'player_id=(\d+)', link['href']).group(1)) for link in contestant_links]
                contestant_names = [link.get_text() for link in contestant_links]
                contestant_ids = await self.get_contestants_by_player_ids(conn, contestant_player_ids, contestant_names)
                # Pad with None if less than 3 contestants
                while len(contestant_ids) < 3:
                    contestant_ids.append(None)
                scores, coryats, winner = self.parse_final_scores(soup, contestant_ids)

                # Check if game already exists
                existing_game = await conn.fetchrow(
                    'SELECT id FROM games WHERE episode_num = $1',
                    episode_num
                )
                if existing_game and not do_upsert:
                    return None

                # Create game record
                # print("CREATING GAME RECORD")
                game_id = await conn.fetchval(
                    '''
                    INSERT INTO games (episode_num, air_date, jarchive_id, season_id, contestant1, contestant2, contestant3, score1, score2, score3, coryat1, coryat2, coryat3, winner)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                    ON CONFLICT (season_id, episode_num, air_date) DO UPDATE
                    SET episode_num = EXCLUDED.episode_num,
                        air_date = EXCLUDED.air_date,
                        jarchive_id = EXCLUDED.jarchive_id,
                        season_id = EXCLUDED.season_id,
                        contestant1 = EXCLUDED.contestant1,
                        contestant2 = EXCLUDED.contestant2,
                        contestant3 = EXCLUDED.contestant3,
                        score1 = EXCLUDED.score1,
                        score2 = EXCLUDED.score2,
                        score3 = EXCLUDED.score3,
                        coryat1 = EXCLUDED.coryat1,
                        coryat2 = EXCLUDED.coryat2,
                        coryat3 = EXCLUDED.coryat3,
                        winner = EXCLUDED.winner
                    RETURNING id
                    ''',
                    episode_num, air_date, jarchive_id, season_id, contestant_ids[0], contestant_ids[1], contestant_ids[2], scores[0], scores[1], scores[2], coryats[0], coryats[1], coryats[2], winner
                )

                # Parse rounds
                await self.parse_round(conn, soup, game_id, "jeopardy_round", "J!")
                await self.parse_round(conn, soup, game_id, "double_jeopardy_round", "DJ!")
                await self.parse_final_jeopardy(conn, soup, game_id)

                # Record that we've parsed this game
                game_link = f"https://www.j-archive.com/showgame.php?game_id={jarchive_id}"
                # print("RECORDING PARSED GAME")
                await conn.execute(
                    '''
                    INSERT INTO parsed_games (episode_num, game_link, game_id, parsed_on)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (episode_num) DO UPDATE
                    SET game_link = EXCLUDED.game_link,
                        game_id = EXCLUDED.game_id
                    ''',
                    episode_num, game_link, game_id, datetime.now()
                )

                return game_id

    def get_clue_value(self, round_type: str, row: int) -> int:
        """Get base clue value based on round and row position."""
        base_values = {
            'J!': 200,    # Jeopardy round base value
            'DJ!': 400,   # Double Jeopardy round base value
        }
        return base_values[round_type] * row


    async def parse_round(self, conn, soup, game_id, round_id, round_name):
        """Parse a regular or double jeopardy round."""
        round_elem = soup.find(id=round_id)
        if not round_elem:
            return

        categories = [c.get_text() for c in round_elem.find_all("td", class_="category_name")]

        for clue_cell in round_elem.find_all("td", class_="clue"):
            if not clue_cell.get_text().strip():
                continue

            clue_text = clue_cell.find("td", class_="clue_text").get_text()
            # returns something like clue_J_5_3 or clue_DJ_1_1
            clue_id = clue_cell.find("td", id=re.compile(r"clue_[D]*J_\d_\d$")).get("id")
            col, row = map(int, clue_id.split('_')[-2:])
            category = categories[col - 1]
            value = self.get_clue_value(round_name, row)

            has_media_link = len(clue_cell.find_all("a", href=re.compile(r'http[s]*://www\.j-archive\.com/media/'))) > 0

            answer = clue_cell.find("em", class_="correct_response").get_text()

            # Check for Daily Double
            daily_double = bool(clue_cell.find("td", class_="clue_value_daily_double"))

            # Handle old-style "no response" for really long ago taped archived games

            await conn.execute(
                '''
                INSERT INTO clues (
                    game_id, value, daily_double, round, category, clue, response, has_media
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ''',
                game_id, value, daily_double, round_name,
                category, clue_text, answer, has_media_link
            )

    async def parse_final_jeopardy(self, conn, soup, game_id):
        """Parse the Final Jeopardy round."""
        final_round = soup.find("table", class_="final_round")
        if not final_round:
            return

        category = final_round.find("td", class_="category_name").get_text()
        clue_text = final_round.find("td", class_="clue_text").get_text()
        answer = final_round.find("em").get_text()

        await conn.execute(
            '''
            INSERT INTO clues (
                game_id, value, daily_double, round, category, clue, response
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            ''',
            game_id, 0, False, 'FJ!', category, clue_text, answer
        )

    async def parse_all_games(self):
        """Parse all game files in the archive directory."""
        await self.init_db_pool()

        files = list(self.archive_dir.glob("*.html"))
        print(f"Found {len(files)} game files to parse")

        pbar = tqdm(files)
        for file_path in pbar:
            try:
                game_id = await self.parse_game_file(file_path, True)
                if game_id:
                    pbar.set_description(f"Parsed game {game_id}")
                else:
                    pbar.set_description(f"Skipped existing game")
            except Exception as e:
                print(f"\nError parsing {file_path}: {e}")
                traceback.print_exc()
                continue

async def main():
    parser = argparse.ArgumentParser(description="Parse Jeopardy! game files into Postgres database")
    parser.add_argument("--dir", default="j-archive", help="Directory containing game HTML files")
    parser.add_argument("--host", default="localhost", help="Database host")
    parser.add_argument("--port", type=int, default=5432, help="Database port")
    parser.add_argument("--user", default="postgres", help="Database user")
    parser.add_argument("--password", required=True, help="Database password")
    parser.add_argument("--database", default="jeopardy", help="Database name")

    args = parser.parse_args()

    db_config = {
        'host': args.host,
        'port': args.port,
        'user': args.user,
        'password': args.password,
        'database': args.database
    }

    parser = JeopardyParser(db_config, args.dir)
    try:
        await parser.parse_all_games()
    finally:
        await parser.close()

if __name__ == "__main__":
    asyncio.run(main())