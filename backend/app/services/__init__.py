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
        # Prefer college-focused hints: colors, conference, mascot (in that order)
        # Field names used in player documents (seeded) are:
        #   - college_colors
        #   - college_conference
        #   - college_mascot
        # If those fields are missing, gracefully fall back to older player info.

        colors = player.get("college_colors") or player.get("colors") or None
        conference = player.get("college_conference") or player.get("conference") or None
        mascot = player.get("college_mascot") or player.get("mascot") or None

        # Friendly label construction with fallbacks
        color_hint = f"College Colors: {colors}" if colors else None
        conference_hint = f"Conference: {conference}" if conference else None
        mascot_hint = f"Mascot: {mascot}" if mascot else None

        # Build ordered list (colors -> conference -> mascot)
        ordered = [h for h in [color_hint, conference_hint, mascot_hint] if h]

        # Difficulty controls how many hints to reveal: easy=3, medium=2, hard=1
        if difficulty == "easy":
            take = 3
        elif difficulty == "medium":
            take = 2
        else:
            take = 1

        hints = ordered[:take]

        # If no college-specific metadata is available, fall back to safer,
        # non-sensitive hints. Do NOT include team, position, league, jersey
        # number, height, or weight per request.
        if not hints:
            draft = player.get('draft_year')
            image_available = 'Yes' if player.get('image_url') else 'No'
            college_meta_available = 'Yes' if (player.get('college_colors') or player.get('college_conference') or player.get('college_mascot')) else 'No'

            # Build fallback candidates (draft year, image availability, college metadata flag)
            fallback_candidates = []
            if draft:
                fallback_candidates.append(f"Draft Year: {draft}")
            fallback_candidates.append(f"Image Available: {image_available}")
            fallback_candidates.append(f"College Metadata Present: {college_meta_available}")

            if difficulty == "easy":
                take = 3
            elif difficulty == "medium":
                take = 2
            else:
                take = 1

            hints = fallback_candidates[:take]

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
