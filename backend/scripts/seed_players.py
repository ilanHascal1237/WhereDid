"""Seed script for WhereDid players collection.

This script connects using app.db.MongoDB (reads MONGODB_URL from env or uses default)
and inserts a small sample set of NBA and NFL players, skipping any that already
exist by exact name match.

Run:
  cd backend
  python .\scripts\seed_players.py
"""

import sys
from pathlib import Path

# Ensure the `backend` directory is on sys.path so `app` package imports work
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db import MongoDB, get_players_collection
from pymongo.errors import PyMongoError
import sys

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
        "college": "St. Vincent–St. Mary"
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
        "college": "N/A"
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
