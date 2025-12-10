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
        "name": "Stephen Curry",
        "draft_year": 2009,
        "image_url": "",
        "college": "Davidson",
        "college_colors": "Red and Black",
        "college_conference": "Atlantic 10",
        "college_mascot": "Wildcats"
    },
    {
        "name": "Patrick Mahomes",
        "draft_year": 2017,
        "image_url": "",
        "college": "Texas Tech",
        "college_colors": "Red and Black",
        "college_conference": "Big 12",
        "college_mascot": "Red Raiders"
    },
    {
        "name": "Derrick Henry",
        "draft_year": 2016,
        "image_url": "",
        "college": "Alabama",
        "college_colors": "Crimson and White",
        "college_conference": "SEC",
        "college_mascot": "Big Al (Elephant)"
    },
    {
        "name": "Kevin Durant",
        "draft_year": 2007,
        "image_url": "",
        "college": "Texas",
        "college_colors": "Burnt Orange and White",
        "college_conference": "Big 12",
        "college_mascot": "Longhorns (Bevo)"
    },
    {
        "name": "Kawhi Leonard",
        "draft_year": 2011,
        "image_url": "",
        "college": "San Diego State",
        "college_colors": "Red and Black",
        "college_conference": "Mountain West",
        "college_mascot": "Aztecs"
    },
    {
        "name": "Joel Embiid",
        "draft_year": 2014,
        "image_url": "",
        "college": "Kansas",
        "college_colors": "Crimson and Blue",
        "college_conference": "Big 12",
        "college_mascot": "Jayhawks"
    },
    {
        "name": "Jayson Tatum",
        "draft_year": 2017,
        "image_url": "",
        "college": "Duke",
        "college_colors": "Royal Blue and White",
        "college_conference": "ACC",
        "college_mascot": "Blue Devils"
    },
    {
        "name": "Tom Brady",
        "draft_year": 2000,
        "image_url": "",
        "college": "Michigan",
        "college_colors": "Maize and Blue",
        "college_conference": "Big Ten",
        "college_mascot": "Wolverines"
    },
    {
        "name": "Aaron Rodgers",
        "draft_year": 2005,
        "image_url": "",
        "college": "California",
        "college_colors": "Blue and Gold",
        "college_conference": "Pac-12",
        "college_mascot": "Golden Bear"
    },
    {
        "name": "Justin Jefferson",
        "draft_year": 2020,
        "image_url": "",
        "college": "LSU",
        "college_colors": "Purple and Gold",
        "college_conference": "SEC",
        "college_mascot": "Mike the Tiger"
    },
    {
        "name": "Saquon Barkley",
        "draft_year": 2018,
        "image_url": "",
        "college": "Penn State",
        "college_colors": "Blue and White",
        "college_conference": "Big Ten",
        "college_mascot": "Nittany Lion"
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
