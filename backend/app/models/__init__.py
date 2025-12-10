from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Player(BaseModel):
    id: str
    name: str
    draft_year: int
    image_url: Optional[str] = None
    college: Optional[str] = None

    class Config:
        populate_by_name = True

class DailyChallenge(BaseModel):
    date: str
    player_id: str
    difficulty: str  # "easy", "medium", "hard"
    created_at: datetime

class GameGuess(BaseModel):
    player_id: str
    guessed_college: str
    difficulty: str

class GuessResponse(BaseModel):
    correct: bool
    message: str
    # Return a plain dict for the player payload so routes can control casing and fields.
    player: Optional[dict] = None
