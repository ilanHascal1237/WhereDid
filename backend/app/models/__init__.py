from pydantic import BaseModel
from typing import Optional

class GameGuess(BaseModel):
    player_id: str
    guessed_college: str
    difficulty: str

class MascotGuess(BaseModel):
    college_id: str
    guessed_college: str
    difficulty: str

class GuessResponse(BaseModel):
    correct: bool
    message: str
    # Return a plain dict for the player payload so routes can control casing and fields.
    player: Optional[dict] = None
