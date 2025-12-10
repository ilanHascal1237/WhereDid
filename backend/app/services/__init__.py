from datetime import datetime
from app.db import get_daily_challenges_collection, get_players_collection
from bson.objectid import ObjectId
import random
import re

class GameService:
    @staticmethod
    def get_daily_challenge(date: str = None):
        """Get the daily challenge for a specific date or today.

        Simplified behavior: every call returns the next player in the
        database (circular rotation). We always generate a new challenge
        and persist it to the `daily_challenges` collection.
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        # Always generate the next player in rotation (circular)
        challenge = GameService._generate_daily_challenge(date)

        return challenge

    @staticmethod
    def _generate_daily_challenge(date: str):
        """Generate the next daily challenge by rotating to the next
        player (circular) based on the most recently created challenge.
        """
        players_collection = get_players_collection()
        challenges_collection = get_daily_challenges_collection()

        # Anchor rotation on the most recent challenge (by created_at).
        last_challenge = challenges_collection.find_one(sort=[("created_at", -1)])
        last_oid = None
        if last_challenge and last_challenge.get("player_id"):
            try:
                last_oid = ObjectId(last_challenge["player_id"])
            except Exception:
                last_oid = None

        player = None

        # Try to select the next player by ObjectId (greater than last).
        if last_oid:
            try:
                next_cursor = players_collection.find({"_id": {"$gt": last_oid}}).sort([("_id", 1)]).limit(1)
                player = next(next_cursor, None)
            except Exception:
                player = None

        # Wrap to the first player if none found
        if not player:
            player = players_collection.find_one(sort=[("_id", 1)])

        if not player:
            raise Exception("No players available in database")

        # Random difficulty for variety
        difficulties = ["easy", "medium", "hard"]
        difficulty = random.choice(difficulties)

        challenge = {
            "date": date,
            "player_id": str(player["_id"]),
            "player": player,
            "difficulty": difficulty,
            "created_at": datetime.now()
        }

        challenges_collection.insert_one(challenge)

        return challenge

    @staticmethod
    def get_hints(player_id: str, difficulty: str):
        """Get hints for a player based on difficulty"""
        players_collection = get_players_collection()
        player = players_collection.find_one({"_id": ObjectId(player_id)})
        
        if not player:
            return []
        
        hints = []
        
        if difficulty == "easy":
            hints = [
                f"League: {player['league']}",
                f"Team: {player['team']}",
                f"Position: {player['position']}",
                f"Jersey Number: {player['jersey_number']}",
                f"Draft Year: {player['draft_year']}"
            ]
        elif difficulty == "medium":
            hints = [
                f"League: {player['league']}",
                f"Team: {player['team']}",
                f"Position: {player['position']}",
                f"Draft Year: {player['draft_year']}"
            ]
        else:  # hard
            hints = [
                f"League: {player['league']}",
                f"Team: {player['team']}",
                f"Position: {player['position']}"
            ]
        
        return hints

    @staticmethod
    def check_guess(player_id: str, guessed_college: str):
        """Check if the guessed college matches the player's college."""
        players_collection = get_players_collection()
        player = players_collection.find_one({"_id": ObjectId(player_id)})

        if not player:
            return False, None

        # Normalize helper: lowercase, strip, remove punctuation
        def _normalize(s: str) -> str:
            s = s or ""
            s = s.lower().strip()
            # Remove punctuation (keep spaces)
            s = re.sub(r"[^a-z0-9\s]", "", s)
            # Collapse whitespace
            s = re.sub(r"\s+", " ", s)
            return s

        normalized_guess = _normalize(guessed_college)
        normalized_college = _normalize(player.get("college", ""))

        if not normalized_college:
            # No college answer available for this player
            return False, None

        # Exact normalized match
        if normalized_guess == normalized_college:
            return True, player

        return False, None
