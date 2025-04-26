import asyncio
import asyncpg
from bs4 import BeautifulSoup
from datetime import datetime
import re
import argparse

async def parse_seasons(html_file, db_config):
    # Read the HTML file
    with open(html_file, 'r', encoding='utf-8') as file:
        content = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(content, 'lxml')
    rows = soup.select('#content table tr')

    # Extract season data
    seasons = []
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 3:
            continue

        season_name = cols[0].get_text(strip=True)
        date_range = cols[1].get_text(strip=True)
        # use regex get the number out of this string '(119 games archived)'
        games_text = cols[2].get_text(strip=True)
        total_games = int(re.search(r'\((\d+) game[s]* archived\)', games_text).group(1))

        try:
            start_date, end_date = date_range.split(' to ')
        except ValueError:
            # Default value for very first season
            start_date = '1983-09-18'
            end_date = '1984-12-31'
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        seasons.append((season_name, start_date, end_date, total_games))

    # Insert data into the database
    conn = await asyncpg.connect(**db_config)
    # TODO: make this an upsert
    await conn.executemany('''
        INSERT INTO seasons (season_name, start_date, end_date, total_games)
        VALUES ($1, $2, $3, $4)
    ''', seasons)
    await conn.close()

async def main():
    parser = argparse.ArgumentParser(description="Parse Jeopardy! season file into Postgres database")
    parser.add_argument("--dir", default='j-archive/seasons/seasons.html', help="Directory containing season HTML file")
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

    await parse_seasons(args.dir, db_config)

if __name__ == "__main__":
    asyncio.run(main())