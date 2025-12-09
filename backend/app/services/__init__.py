from datetime import datetime
from app.db import get_daily_challenges_collection, get_players_collection
from bson.objectid import ObjectId
import random

class GameService:
    @staticmethod
    def get_daily_challenge(date: str = None):
        """Get the daily challenge for a specific date or today"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        challenges_collection = get_daily_challenges_collection()
        challenge = challenges_collection.find_one({"date": date})
        
        if not challenge:
            # Generate new daily challenge
            challenge = GameService._generate_daily_challenge(date)
        
        return challenge

    @staticmethod
    def _generate_daily_challenge(date: str):
        """Generate a new daily challenge"""
        players_collection = get_players_collection()
        
        # Get random player
        random_player = players_collection.aggregate([
            {"$sample": {"size": 1}}
        ])
        player = next(random_player, None)
        
        if not player:
            raise Exception("No players available in database")
        
        # Randomly select difficulty
        difficulties = ["easy", "medium", "hard"]
        difficulty = random.choice(difficulties)
        
        # Create challenge
        challenge = {
            "date": date,
            "player_id": str(player["_id"]),
            "player": player,
            "difficulty": difficulty,
            "created_at": datetime.now()
        }
        
        # Save to database
        challenges_collection = get_daily_challenges_collection()
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
    def check_guess(player_id: str, guessed_name: str):
        """Check if guess is correct"""
        players_collection = get_players_collection()
        player = players_collection.find_one({"_id": ObjectId(player_id)})
        
        if not player:
            return False
        
        # Case-insensitive comparison
        return player["name"].lower().strip() == guessed_name.lower().strip()
