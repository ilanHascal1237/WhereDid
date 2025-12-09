from fastapi import APIRouter, HTTPException
from app.services import GameService
from app.models import GuessResponse

router = APIRouter(prefix="/game", tags=["game"])

@router.get("/daily-challenge")
async def get_daily_challenge():
    """Get today's daily challenge"""
    try:
        challenge = GameService.get_daily_challenge()
        player = challenge.get("player", {})
        return {
            "date": challenge["date"],
            "player": {
                "id": str(player.get("_id")) if player.get("_id") is not None else None,
                "name": player.get("name"),
                "team": player.get("team"),
                "position": player.get("position"),
                "league": player.get("league"),
                "jerseyNumber": player.get("jersey_number"),
                "draftYear": player.get("draft_year"),
            },
            "difficulty": challenge["difficulty"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hints/{player_id}")
async def get_hints(player_id: str, difficulty: str):
    """Get hints for a player"""
    try:
        hints = GameService.get_hints(player_id, difficulty)
        return {"hints": hints}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/guess", response_model=GuessResponse)
async def submit_guess(player_id: str, guessed_player_name: str, difficulty: str):
    """Submit a guess"""
    try:
        is_correct = GameService.check_guess(player_id, guessed_player_name)
        
        if is_correct:
            return GuessResponse(
                correct=True,
                message="Correct! You got it!"
            )
        else:
            return GuessResponse(
                correct=False,
                message=f"Incorrect. '{guessed_player_name}' is not the right player."
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
