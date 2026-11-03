"""Sync NBA and NFL players from ESPN into the players collection.

Run:
    cd backend
    python ./scripts/sync_players.py            # both leagues
    python ./scripts/sync_players.py NBA        # one league
"""

import sys
from pathlib import Path

# Ensure the `backend` directory is on sys.path so `app` package imports work
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
from app.db import MongoDB
from app.services.espn import LEAGUES, sync_players


def main():
    load_dotenv(ROOT / ".env")
    leagues = [arg.upper() for arg in sys.argv[1:]] or None
    for league in leagues or []:
        if league not in LEAGUES:
            print(f"Unknown league '{league}'. Choose from: {', '.join(LEAGUES)}")
            sys.exit(1)

    try:
        MongoDB.connect_db()
        sync_players(leagues)
    except Exception as e:
        print("Sync failed:", str(e))
        sys.exit(1)
    finally:
        MongoDB.close_db()


if __name__ == "__main__":
    main()
