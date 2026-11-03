import re
from typing import Optional

from fastapi import APIRouter, HTTPException
from app.db import get_players_collection
from app.services import public_player
from bson.objectid import ObjectId

router = APIRouter(prefix="/players", tags=["players"])

MAX_QUERY_LENGTH = 100

@router.get("/search")
async def search_players(q: str):
    """Search for players by name"""
    if len(q) > MAX_QUERY_LENGTH:
        raise HTTPException(status_code=400, detail=f"Query too long (max {MAX_QUERY_LENGTH} characters)")
    players_collection = get_players_collection()
    # Only return minimal public fields (id + name). Do not expose team/position/league/jersey/height/weight.
    results = list(players_collection.find(
        {"name": {"$regex": re.escape(q), "$options": "i"}},
        {"_id": 1, "name": 1}
    ).limit(10))

    players = [
        {
            "id": str(p["_id"]),
            "name": p["name"]
        }
        for p in results
    ]

    return {"players": players}


@router.get("/colleges")
async def get_colleges(q: Optional[str] = None):
    """Return a list of distinct college names (optionally filtered by a query).

    This helps the frontend provide type-ahead suggestions for college names.
    """
    if q is not None and len(q) > MAX_QUERY_LENGTH:
        raise HTTPException(status_code=400, detail=f"Query too long (max {MAX_QUERY_LENGTH} characters)")
    players_collection = get_players_collection()
    query = {"college": {"$ne": None}}
    if q:
        # case-insensitive substring match
        query = {"college": {"$regex": re.escape(q), "$options": "i"}}

    # Use distinct to get unique college names
    colleges = players_collection.distinct("college", query)
    # Filter out empty/null and ensure strings
    colleges = [c for c in colleges if isinstance(c, str) and c.strip()]
    # Optionally sort for consistent ordering
    colleges.sort()
    return {"colleges": colleges}


@router.get("/{player_id}")
async def get_player(player_id: str):
    """Get player details by ID"""
    players_collection = get_players_collection()
    # Validate player_id as ObjectId; if invalid, return 404 instead of 500
    try:
        oid = ObjectId(player_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Player not found")

    player = players_collection.find_one({"_id": oid})

    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    # Do NOT return the `college` field here — the game requires the client
    # to guess the college. The DB still stores the college value for checking
    # guesses, but we omit it from the player payload sent to the UI.
    # Only expose non-sensitive public fields. College is intentionally omitted.
    return public_player(player)
