from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Player(BaseModel):
    id: str
    name: str
    team: str
    position: str
    league: str  # "NBA" or "NFL"
    jersey_number: int
    draft_year: int
    image_url: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[int] = None
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
    guessed_player_name: str
    difficulty: str

class GuessResponse(BaseModel):
    correct: bool
    message: str
    player: Optional[Player] = None
