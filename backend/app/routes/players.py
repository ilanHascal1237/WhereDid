from fastapi import APIRouter, HTTPException
from app.db import get_players_collection
from bson.objectid import ObjectId

router = APIRouter(prefix="/players", tags=["players"])

@router.get("/search")
async def search_players(q: str):
    """Search for players by name"""
    try:
        players_collection = get_players_collection()
        results = list(players_collection.find(
            {"name": {"$regex": q, "$options": "i"}},
            {"_id": 1, "name": 1, "team": 1, "league": 1, "position": 1}
        ).limit(10))
        
        players = [
            {
                "id": str(p["_id"]),
                "name": p["name"],
                "team": p.get("team"),
                "league": p.get("league"),
                "position": p.get("position")
            }
            for p in results
        ]
        
        return {"players": players}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{player_id}")
async def get_player(player_id: str):
    """Get player details by ID"""
    try:
        players_collection = get_players_collection()
        player = players_collection.find_one({"_id": ObjectId(player_id)})
        
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        # Do NOT return the `college` field here — the game requires the client
        # to guess the college. The DB still stores the college value for checking
        # guesses, but we omit it from the player payload sent to the UI.
        payload = {
            "id": str(player["_id"]),
            "name": player["name"],
            "team": player["team"],
            "position": player["position"],
            "league": player["league"],
            "jerseyNumber": player.get("jersey_number"),
            "draftYear": player.get("draft_year"),
            "height": player.get("height"),
            "weight": player.get("weight"),
            "imageUrl": player.get("image_url")
        }

        return payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
