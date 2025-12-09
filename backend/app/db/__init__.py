from pymongo import MongoClient
from typing import Optional
import os

class MongoDB:
    client: Optional[MongoClient] = None
    db = None

    @classmethod
    def connect_db(cls):
        """Connect to MongoDB"""
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        database_name = os.getenv("DATABASE_NAME", "wheredid")
        
        cls.client = MongoClient(mongodb_url)
        cls.db = cls.client[database_name]
        print(f"Connected to MongoDB database: {database_name}")

    @classmethod
    def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            print("Closed MongoDB connection")

    @classmethod
    def get_db(cls):
        """Get database instance"""
        if cls.db is None:
            cls.connect_db()
        return cls.db

# Initialize collections
def get_players_collection():
    db = MongoDB.get_db()
    return db["players"]

def get_daily_challenges_collection():
    db = MongoDB.get_db()
    return db["daily_challenges"]

def get_game_sessions_collection():
    db = MongoDB.get_db()
    return db["game_sessions"]
