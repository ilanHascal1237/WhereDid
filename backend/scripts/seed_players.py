"""Seed script for WhereDid players collection.

This script connects using app.db.MongoDB (reads MONGODB_URL from env or uses default)
and inserts a sample set of players, skipping any that already exist by exact name match.

Run:
    cd backend
    python ./scripts/seed_players.py
"""

import sys
from pathlib import Path

# Ensure the `backend` directory is on sys.path so `app` package imports work
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

from app.db import MongoDB, get_players_collection
from pymongo.errors import PyMongoError

# Expanded sample players. Seed includes accurate `college` values (or None when
# the player did not attend college). The routes are configured to omit the
# `college` field in the public player payload so the UI must prompt the user
# to guess it.
sample_players = [
    {
        "name": "LeBron James",
        "team": "LAL",
        "position": "SF",
        "league": "NBA",
        "jersey_number": 6,
        "draft_year": 2003,
        "image_url": "",
        "height": "6 ft 9 in",
        "weight": 250,
        "college": None
    },
    {
        "name": "Stephen Curry",
        "team": "GSW",
        "position": "PG",
        "league": "NBA",
        "jersey_number": 30,
        "draft_year": 2009,
        "image_url": "",
        "height": "6 ft 2 in",
        "weight": 190,
        "college": "Davidson"
    },
    {
        "name": "Giannis Antetokounmpo",
        "team": "MIL",
        "position": "PF",
        "league": "NBA",
        "jersey_number": 34,
        "draft_year": 2013,
        "image_url": "",
        "height": "6 ft 11 in",
        "weight": 242,
        "college": None
    },
    {
        "name": "Patrick Mahomes",
        "team": "KC",
        "position": "QB",
        "league": "NFL",
        "jersey_number": 15,
        "draft_year": 2017,
        "image_url": "",
        "height": "6 ft 2 in",
        "weight": 225,
        "college": "Texas Tech"
    },
    {
        "name": "Derrick Henry",
        "team": "TEN",
        "position": "RB",
        "league": "NFL",
        "jersey_number": 22,
        "draft_year": 2016,
        "image_url": "",
        "height": "6 ft 3 in",
        "weight": 247,
        "college": "Alabama"
    },
    {
        "name": "Luka Doncic",
        "team": "DAL",
        "position": "PG",
        "league": "NBA",
        "jersey_number": 77,
        "draft_year": 2018,
        "image_url": "",
        "height": "6 ft 7 in",
        "weight": 230,
        "college": None
    },
    {
        "name": "Kevin Durant",
        "team": "PHX",
        "position": "SF",
        "league": "NBA",
        "jersey_number": 35,
        "draft_year": 2007,
        "image_url": "",
        "height": "6 ft 10 in",
        "weight": 240,
        "college": "Texas"
    },
    {
        "name": "Kawhi Leonard",
        "team": "LAC",
        "position": "SF",
        "league": "NBA",
        "jersey_number": 2,
        "draft_year": 2011,
        "image_url": "",
        "height": "6 ft 7 in",
        "weight": 225,
        "college": "San Diego State"
    },
    {
        "name": "Joel Embiid",
        "team": "PHI",
        "position": "C",
        "league": "NBA",
        "jersey_number": 21,
        "draft_year": 2014,
        "image_url": "",
        "height": "7 ft 0 in",
        "weight": 280,
        "college": "Kansas"
    },
    {
        "name": "Jayson Tatum",
        "team": "BOS",
        "position": "SF",
        "league": "NBA",
        "jersey_number": 0,
        "draft_year": 2017,
        "image_url": "",
        "height": "6 ft 8 in",
        "weight": 210,
        "college": "Duke"
    },
    {
        "name": "Tom Brady",
        "team": "TB",
        "position": "QB",
        "league": "NFL",
        "jersey_number": 12,
        "draft_year": 2000,
        "image_url": "",
        "height": "6 ft 4 in",
        "weight": 225,
        "college": "Michigan"
    },
    {
        "name": "Aaron Rodgers",
        "team": "NYJ",
        "position": "QB",
        "league": "NFL",
        "jersey_number": 8,
        "draft_year": 2005,
        "image_url": "",
        "height": "6 ft 2 in",
        "weight": 225,
        "college": "California"
    },
    {
        "name": "Justin Jefferson",
        "team": "MIN",
        "position": "WR",
        "league": "NFL",
        "jersey_number": 18,
        "draft_year": 2020,
        "image_url": "",
        "height": "6 ft 1 in",
        "weight": 202,
        "college": "LSU"
    },
    {
        "name": "Saquon Barkley",
        "team": "PHI",
        "position": "RB",
        "league": "NFL",
        "jersey_number": 26,
        "draft_year": 2018,
        "image_url": "",
        "height": "6 ft 0 in",
        "weight": 233,
        "college": "Penn State"
    },
    {
        "name": "A'ja Wilson",
        "team": "LAS",
        "position": "F",
        "league": "WNBA",
        "jersey_number": 22,
        "draft_year": 2018,
        "image_url": "",
        "height": "6 ft 4 in",
        "weight": 195,
        "college": "South Carolina"
    }
]
 


def seed():
    try:
        MongoDB.connect_db()
        coll = get_players_collection()

        inserted = 0
        skipped = 0
        for p in sample_players:
            # Use exact name match to avoid duplicates
            existing = coll.find_one({"name": p["name"]})
            if existing:
                print(f"Skipping existing player: {p['name']}")
                skipped += 1
                continue

            result = coll.insert_one(p)
            if result.inserted_id:
                print(f"Inserted: {p['name']} (id={result.inserted_id})")
                inserted += 1

        print(f"Seeding complete. Inserted: {inserted}. Skipped: {skipped}.")

    except PyMongoError as e:
        print("MongoDB error during seeding:", str(e))
        sys.exit(1)
    except Exception as e:
        print("Unexpected error during seeding:", str(e))
        sys.exit(1)
    finally:
        MongoDB.close_db()


if __name__ == "__main__":
    seed()
