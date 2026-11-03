from datetime import datetime
from app.db import get_daily_challenges_collection, get_players_collection
from bson.objectid import ObjectId
import hashlib
import random
import re


class DataNotReadyError(Exception):
    """Raised when a request can't be served because backing data (e.g.
    player/college records) hasn't finished syncing yet. This is a transient
    "not ready" condition, not a server bug, and is mapped to a 503 response
    by the global exception handler in main.py."""


# Per-difficulty rules:
#   hints          - how many college hints are revealed
#   max_guesses    - attempts allowed in daily mode
#   min_experience - endless mode only draws players with at least this many
#                    pro seasons, so easy mode sticks to well-known veterans
DIFFICULTIES = {
    "easy": {"hints": 3, "max_guesses": 6, "min_experience": 8},
    "medium": {"hints": 2, "max_guesses": 4, "min_experience": 4},
    "hard": {"hints": 1, "max_guesses": 3, "min_experience": 1},
}

# The daily player is drawn from established players only
DAILY_MIN_EXPERIENCE = 7

# Long snappers and punters are too obscure to be fair guesses
EXCLUDED_POSITIONS = ["LS", "P"]

LEAGUES = ["NBA", "NFL"]

# Mascot mode rules:
#   hints       - extra clues shown alongside the mascot
#   min_players - only schools with at least this many current pros, so easy
#                 mode sticks to big programs
MASCOT_DIFFICULTIES = {
    "easy": {"hints": 2, "min_players": 15},
    "medium": {"hints": 1, "min_players": 5},
    "hard": {"hints": 0, "min_players": 1},
}


def difficulty_rules(difficulty: str) -> dict:
    return DIFFICULTIES.get(difficulty, DIFFICULTIES["medium"])


def public_player(player: dict, reveal: bool = False) -> dict:
    """Player payload for the UI. The college is only included when revealed."""
    payload = {
        "id": str(player["_id"]),
        "name": player.get("name"),
        "league": player.get("league"),
        "imageUrl": player.get("image_url"),
    }
    if reveal:
        payload["college"] = player.get("college")
        payload["collegeLogo"] = player.get("college_logo")
    return payload


def _normalize(s: str) -> str:
    """Lowercase, drop punctuation and filler words like 'university of'."""
    s = (s or "").lower().strip()
    s = s.replace("&", " and ")
    s = re.sub(r"[^a-z0-9\s]", "", s)
    s = re.sub(r"\b(the|university|of|college)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _answer_forms(player: dict) -> set:
    """All accepted spellings of a player's college."""
    names = [player.get("college")] + list(player.get("college_aliases") or [])
    forms = set()
    for name in names:
        if not name:
            continue
        forms.add(_normalize(name))
        # 'Miami (FL)' should also accept 'Miami'
        forms.add(_normalize(re.sub(r"\(.*?\)", "", name)))
    forms.discard("")
    return forms


def _find_player(player_id: str):
    try:
        oid = ObjectId(player_id)
    except Exception:
        return None
    return get_players_collection().find_one({"_id": oid})


class GameService:
    @staticmethod
    def get_daily_challenge(date: str = None):
        """Return the mystery player for a date (YYYY-MM-DD), today by default.

        The first request for a date picks a player deterministically from the
        date and stores it, so every request that day gets the same player.
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        challenges_collection = get_daily_challenges_collection()
        existing = challenges_collection.find_one({"kind": "daily", "date": date})
        if existing:
            player = _find_player(existing["player_id"])
            if player:
                return {"date": date, "player": player}
            # Player was removed by a re-sync; pick a new one for the date
            challenges_collection.delete_one({"_id": existing["_id"]})

        player = GameService._pick_daily_player(date)
        challenges_collection.insert_one({
            "kind": "daily",
            "date": date,
            "player_id": str(player["_id"]),
            "created_at": datetime.now(),
        })
        return {"date": date, "player": player}

    @staticmethod
    def _pick_daily_player(date: str):
        players_collection = get_players_collection()
        seed = int(hashlib.sha256(date.encode()).hexdigest(), 16)

        # NFL rosters are ~5x larger, so pick the league first to keep the
        # daily player split evenly between NBA and NFL
        base_query = {
            "college": {"$ne": None},
            "experience": {"$gte": DAILY_MIN_EXPERIENCE},
            "position": {"$nin": EXCLUDED_POSITIONS},
        }
        league_query = {**base_query, "league": LEAGUES[seed % len(LEAGUES)]}

        # Fall back to broader pools (e.g. only one league synced)
        for query in (league_query, base_query, {"college": {"$ne": None}}):
            count = players_collection.count_documents(query)
            if count:
                break
        else:
            raise DataNotReadyError("No players available yet. Player data may still be syncing.")

        index = (seed // len(LEAGUES)) % count
        return next(players_collection.find(query).sort("_id", 1).skip(index).limit(1))

    @staticmethod
    def get_random_player(league: str = None, difficulty: str = "medium", exclude: list = None):
        """Random player for endless mode, skipping ids already seen this run."""
        rules = difficulty_rules(difficulty)
        match = {
            "college": {"$ne": None},
            "experience": {"$gte": rules["min_experience"]},
            "position": {"$nin": EXCLUDED_POSITIONS},
        }
        if league in LEAGUES:
            match["league"] = league

        exclude_oids = []
        for pid in exclude or []:
            try:
                exclude_oids.append(ObjectId(pid))
            except Exception:
                continue
        if exclude_oids:
            match["_id"] = {"$nin": exclude_oids}

        players_collection = get_players_collection()
        result = list(players_collection.aggregate([{"$match": match}, {"$sample": {"size": 1}}]))
        if not result and exclude_oids:
            # Pool exhausted for this run; allow repeats
            del match["_id"]
            result = list(players_collection.aggregate([{"$match": match}, {"$sample": {"size": 1}}]))
        if not result:
            raise Exception("No players available for this league and difficulty")
        return result[0]

    @staticmethod
    def get_hints(player_id: str, difficulty: str):
        """College hints for a player; difficulty controls how many."""
        player = _find_player(player_id)
        if not player:
            return []

        colors = player.get("college_colors")
        conference = player.get("college_conference")
        mascot = player.get("college_mascot")
        college = player.get("college") or ""

        # Ordered from vaguest to most revealing
        ordered = [
            f"College Colors: {colors}" if colors else None,
            f"Conference: {conference}" if conference else None,
            f"Mascot: {mascot}" if mascot else None,
        ]
        hints = [h for h in ordered if h]

        # Pad with spelling hints when college metadata is missing
        if college:
            hints.append(f"Starts with the letter '{college[0].upper()}'")
            hints.append(f"{len(college.split())} word(s), {len(college.replace(' ', ''))} letters")

        return hints[:difficulty_rules(difficulty)["hints"]]

    @staticmethod
    def check_guess(player_id: str, guessed_college: str):
        """Check if the guessed college matches the player's college."""
        player = _find_player(player_id)
        if not player:
            return False, None

        if _normalize(guessed_college) in _answer_forms(player):
            return True, player
        return False, player

    @staticmethod
    def get_player(player_id: str):
        return _find_player(player_id)


# Cached result of _college_groups(match=None) - the "all colleges" grouping
# used by MascotService on every /game/mascot/next and /game/mascot/guess
# request. The underlying data only changes when an ESPN sync runs, so this
# is invalidated via invalidate_college_cache() rather than on a timer.
_college_groups_cache: list = None


def invalidate_college_cache() -> None:
    """Drop the cached college groups so the next lookup re-reads Mongo.

    Call this after a player sync (e.g. espn.sync_players) completes, since
    that's the only thing that changes the data _college_groups() reflects.
    """
    global _college_groups_cache
    _college_groups_cache = None


def _college_groups(match: dict = None) -> list:
    """One document per college, built from the players collection.

    The no-filter "all colleges" case (match=None) is cached in-process
    since it's recomputed on every mascot-mode request; a single-college
    lookup (match={"college_espn_id": ...}) is cheap/targeted already and
    isn't cached.
    """
    global _college_groups_cache
    if match is None and _college_groups_cache is not None:
        return _college_groups_cache

    pipeline = [
        {"$match": {"college_espn_id": {"$ne": None}, **(match or {})}},
        {"$group": {
            "_id": "$college_espn_id",
            "college": {"$first": "$college"},
            "college_aliases": {"$first": "$college_aliases"},
            "mascot": {"$first": "$college_mascot"},
            "colors": {"$first": "$college_colors"},
            "conference": {"$first": "$college_conference"},
            "logo": {"$first": "$college_logo"},
            "players": {"$sum": 1},
        }},
    ]
    result = list(get_players_collection().aggregate(pipeline))

    if match is None:
        _college_groups_cache = result
    return result


def _mascot_clues(college: dict, difficulty: str) -> list:
    """(field, label) pairs shown with the mascot, most useful first."""
    clues = [("conference", "Conference"), ("colors", "College Colors")]
    clues = [(field, label) for field, label in clues if college.get(field)]
    return clues[:MASCOT_DIFFICULTIES.get(difficulty, MASCOT_DIFFICULTIES["medium"])["hints"]]


def public_college(college: dict, reveal: bool = False) -> dict:
    payload = {"id": college["_id"], "mascot": college.get("mascot")}
    if reveal:
        payload["college"] = college.get("college")
        payload["logo"] = college.get("logo")
    return payload


class MascotService:
    @staticmethod
    def get_round(difficulty: str = "medium", exclude: list = None):
        """Random college whose mascot the user must match to a school."""
        rules = MASCOT_DIFFICULTIES.get(difficulty, MASCOT_DIFFICULTIES["medium"])
        colleges = [
            c for c in _college_groups()
            if c.get("mascot") and c["players"] >= rules["min_players"]
        ]
        fresh = [c for c in colleges if c["_id"] not in set(exclude or [])]
        pool = fresh or colleges  # allow repeats once the pool is exhausted
        if not pool:
            raise DataNotReadyError("No colleges available yet. Player data may still be syncing.")

        college = random.choice(pool)
        hints = [f"{label}: {college[field]}" for field, label in _mascot_clues(college, difficulty)]
        return college, hints

    @staticmethod
    def check_guess(college_id: str, guessed_college: str, difficulty: str):
        """Correct if the guess is any school consistent with every clue shown.

        Mascots repeat (there are many Bulldogs), so on hard mode any school
        with the same mascot counts; on easier modes the shown conference /
        colors must match too.
        """
        target = next(iter(_college_groups({"college_espn_id": college_id})), None)
        if not target:
            return False, None

        shown_fields = [field for field, _ in _mascot_clues(target, difficulty)]
        candidates = [
            c for c in _college_groups({"college_mascot": target["mascot"]})
            if all(c.get(f) == target.get(f) for f in shown_fields)
        ]

        guess = _normalize(guessed_college)
        for c in candidates:
            if guess in _answer_forms(c):
                return True, c
        return False, target
