from typing import Optional
from fastapi import APIRouter, HTTPException
from app.services import GameService, MascotService, difficulty_rules, public_college, public_player
from app.models import GuessResponse, GameGuess, MascotGuess

router = APIRouter(prefix="/game", tags=["game"])

@router.get("/daily-challenge")
async def get_daily_challenge(date: str = None, difficulty: str = "medium"):
    """Get the daily challenge for a specific date (YYYY-MM-DD) or today if no date provided.

    Every request for the same date returns the same player. The college is
    intentionally omitted so the client must guess it.
    """
    try:
        challenge = GameService.get_daily_challenge(date)
        rules = difficulty_rules(difficulty)
        return {
            "date": challenge["date"],
            "player": public_player(challenge["player"]),
            "difficulty": difficulty if difficulty in ("easy", "medium", "hard") else "medium",
            "maxGuesses": rules["max_guesses"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/endless/next")
async def get_endless_player(
    league: Optional[str] = None,
    difficulty: str = "medium",
    exclude: Optional[str] = None,
):
    """Random player for endless mode.

    `league` is NBA, NFL or omitted for both. `exclude` is a comma-separated
    list of player ids already shown this run.
    """
    try:
        player = GameService.get_random_player(
            league=league,
            difficulty=difficulty,
            exclude=exclude.split(",") if exclude else [],
        )
        return {
            "player": public_player(player),
            "hints": GameService.get_hints(str(player["_id"]), difficulty),
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

        if player is None:
            raise HTTPException(status_code=404, detail="Player not found")

        if is_correct:
            return GuessResponse(
                correct=True,
                message="Correct! You got it!",
                player=public_player(player, reveal=True)
            )
        return GuessResponse(
            correct=False,
            message=f"Incorrect. '{guess.guessed_college}' is not the correct college."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mascot/next")
async def get_mascot_round(difficulty: str = "medium", exclude: Optional[str] = None):
    """Random college mascot to identify. `exclude` is a comma-separated list
    of college ids already shown this run."""
    try:
        college, hints = MascotService.get_round(
            difficulty=difficulty,
            exclude=exclude.split(",") if exclude else [],
        )
        return {"college": public_college(college), "hints": hints}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mascot/guess")
async def submit_mascot_guess(guess: MascotGuess):
    """Guess which school a mascot belongs to. Always reveals the answer,
    since each mascot round is a single guess."""
    try:
        is_correct, college = MascotService.check_guess(
            guess.college_id, guess.guessed_college, guess.difficulty
        )
        if college is None:
            raise HTTPException(status_code=404, detail="College not found")
        return {"correct": is_correct, "college": public_college(college, reveal=True)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reveal/{player_id}")
async def reveal_answer(player_id: str):
    """Reveal a player's college once the round is over (out of guesses or skipped)."""
    player = GameService.get_player(player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return public_player(player, reveal=True)
