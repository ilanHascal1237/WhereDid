from fastapi import APIRouter, HTTPException
from app.db import get_players_collection
from bson.objectid import ObjectId

router = APIRouter(prefix="/players", tags=["players"])

@router.get("/search")
async def search_players(q: str):
    """Search for players by name"""
    try:
        players_collection = get_players_collection()
        # Only return minimal public fields (id + name). Do not expose team/position/league/jersey/height/weight.
        results = list(players_collection.find(
            {"name": {"$regex": q, "$options": "i"}},
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/colleges")
async def get_colleges(q: str = None):
    """Return a list of distinct college names (optionally filtered by a query).

    This helps the frontend provide type-ahead suggestions for college names.
    """
    try:
        players_collection = get_players_collection()
        query = {"college": {"$ne": None}}
        if q:
            # case-insensitive substring match
            query = {"college": {"$regex": q, "$options": "i"}}

        # Use distinct to get unique college names
        colleges = players_collection.distinct("college", query)
        # Filter out empty/null and ensure strings
        colleges = [c for c in colleges if isinstance(c, str) and c.strip()]
        # Optionally sort for consistent ordering
        colleges.sort()
        return {"colleges": colleges}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@router.get("/{player_id}")
async def get_player(player_id: str):
    """Get player details by ID"""
    try:
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
        payload = {
            "id": str(player["_id"]),
            "name": player["name"],
            "draftYear": player.get("draft_year"),
            "imageUrl": player.get("image_url")
        }

        return payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
