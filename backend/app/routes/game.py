from fastapi import APIRouter, HTTPException
from app.services import GameService
from app.models import GuessResponse, GameGuess, Player

router = APIRouter(prefix="/game", tags=["game"])

@router.get("/daily-challenge")
async def get_daily_challenge(date: str = None):
    """Get the daily challenge for a specific date (YYYY-MM-DD) or today if no date provided.

    Behavior: each call returns the next player in the DB in a circular rotation.
    """
    try:
        # Always generate the next challenge (rotate to next player)
        challenge = GameService.get_daily_challenge(date)
        player = challenge.get("player", {})
        # Only expose minimal public fields: id, name, and team.
        # The college is intentionally omitted so the client must guess it.
        return {
            "date": challenge["date"],
            "player": {
                "id": str(player.get("_id")) if player.get("_id") is not None else None,
                "name": player.get("name"),
                "team": player.get("team"),
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
async def submit_guess(guess: GameGuess):
    """Submit a guess (body: GameGuess). The client should send the guessed_college."""
    try:
        is_correct, player = GameService.check_guess(guess.player_id, guess.guessed_college)

        if is_correct:
            # Map DB player document to Player model expected by GuessResponse
            player_obj = Player(
                id=str(player.get("_id")) if player.get("_id") is not None else None,
                name=player.get("name"),
                team=player.get("team"),
                position=player.get("position"),
                league=player.get("league"),
                jersey_number=player.get("jersey_number"),
                draft_year=player.get("draft_year"),
                image_url=player.get("image_url"),
                height=player.get("height"),
                weight=player.get("weight"),
                college=player.get("college")
            )

            return GuessResponse(
                correct=True,
                message="Correct! You got it!",
                player=player_obj
            )
        else:
            return GuessResponse(
                correct=False,
                message=f"Incorrect. '{guess.guessed_college}' is not the correct college."
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
