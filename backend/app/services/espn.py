"""Player ingestion from ESPN's public site API.

Fetches every NBA and NFL team roster, keeps players that have a college on
record, enriches each college with colors + conference, and upserts the
result into the `players` collection keyed by `espn_id`.
"""

import json
import re
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Optional

from pymongo import UpdateOne

from app.db import get_players_collection

BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"

LEAGUES = {
    "NBA": "basketball/nba",
    "NFL": "football/nfl",
}

# College team lookups. A school's conference can differ by sport (Davidson
# plays Pioneer League football but Atlantic 10 basketball), so each league
# prefers the conference of its own college sport.
COLLEGE_SPORTS = {
    "NFL": "football/college-football",
    "NBA": "basketball/mens-college-basketball",
}

# NFL roster groups that are not part of the active roster
SKIPPED_NFL_GROUPS = {"practiceSquad"}

# Players are considered stale and re-synced after this long
SYNC_MAX_AGE = timedelta(days=7)

# Named colors used to turn ESPN hex values into readable hints
NAMED_COLORS = {
    "Black": (0, 0, 0),
    "White": (255, 255, 255),
    "Gray": (128, 128, 128),
    "Silver": (192, 192, 192),
    "Red": (220, 20, 30),
    "Crimson": (158, 27, 50),
    "Maroon": (110, 20, 40),
    "Orange": (255, 120, 0),
    "Burnt Orange": (191, 87, 0),
    "Gold": (200, 160, 50),
    "Yellow": (255, 210, 0),
    "Green": (0, 128, 60),
    "Dark Green": (0, 70, 40),
    "Navy": (0, 34, 85),
    "Royal Blue": (0, 60, 160),
    "Light Blue": (100, 170, 230),
    "Purple": (80, 40, 130),
    "Brown": (100, 60, 30),
    "Teal": (0, 128, 128),
}


def _get_json(url: str, retries: int = 2) -> Optional[dict]:
    """GET a JSON document, returning None on 404 or repeated failure."""
    req = urllib.request.Request(url, headers={"User-Agent": "WhereDid/0.1"})
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            pass
        time.sleep(0.5 * (attempt + 1))
    return None


def _color_name(hex_value: Optional[str]) -> Optional[str]:
    """Map a hex color like 'e00122' to the nearest named color."""
    if not hex_value or not re.fullmatch(r"[0-9a-fA-F]{6}", hex_value):
        return None
    rgb = tuple(int(hex_value[i:i + 2], 16) for i in (0, 2, 4))
    return min(
        NAMED_COLORS,
        key=lambda name: sum((a - b) ** 2 for a, b in zip(rgb, NAMED_COLORS[name])),
    )


def _parse_conference(standing_summary: Optional[str]) -> Optional[str]:
    """'1st in SEC - East' -> 'SEC'"""
    if not standing_summary or " in " not in standing_summary:
        return None
    conference = standing_summary.split(" in ", 1)[1]
    return conference.split(" - ")[0].strip() or None


def fetch_team_ids(league: str) -> list:
    data = _get_json(f"{BASE_URL}/{LEAGUES[league]}/teams") or {}
    teams = data.get("sports", [{}])[0].get("leagues", [{}])[0].get("teams", [])
    return [t["team"]["id"] for t in teams]


def fetch_roster(league: str, team_id: str) -> list:
    """Return raw athlete dicts (with team name attached) for one team."""
    data = _get_json(f"{BASE_URL}/{LEAGUES[league]}/teams/{team_id}/roster")
    if not data:
        return []

    team_name = data.get("team", {}).get("displayName")
    athletes = []
    for entry in data.get("athletes", []):
        # NBA rosters are a flat list; NFL rosters are grouped by unit
        if "items" in entry:
            if entry.get("position") in SKIPPED_NFL_GROUPS:
                continue
            athletes.extend(entry["items"])
        else:
            athletes.append(entry)

    for a in athletes:
        a["_team_name"] = team_name
    return athletes


def fetch_college(college_id: str) -> dict:
    """Colors and per-league conference for a college."""
    info = {"colors_hex": [], "conferences": {}, "display_name": None}
    for league, sport in COLLEGE_SPORTS.items():
        data = _get_json(f"{BASE_URL}/{sport}/teams/{college_id}")
        team = (data or {}).get("team")
        if not team:
            continue
        if not info["colors_hex"]:
            info["colors_hex"] = [c for c in (team.get("color"), team.get("alternateColor")) if c]
        info["display_name"] = info["display_name"] or team.get("displayName")
        info["conferences"][league] = _parse_conference(team.get("standingSummary"))
    return info


def _build_player(athlete: dict, league: str, college_info: dict) -> dict:
    college = athlete["college"]
    color_names = []
    for hex_value in college_info.get("colors_hex", []):
        name = _color_name(hex_value)
        if name and name not in color_names:
            color_names.append(name)

    conferences = college_info.get("conferences", {})
    other_league = next(l for l in COLLEGE_SPORTS if l != league)
    conference = conferences.get(league) or conferences.get(other_league)

    aliases = {
        college.get("name"),
        college.get("shortName"),
        college.get("abbrev"),
        college_info.get("display_name"),
    }

    return {
        "espn_id": athlete["id"],
        "source": "espn",
        "name": athlete.get("displayName") or athlete.get("fullName"),
        "league": league,
        "team": athlete.get("_team_name"),
        "position": (athlete.get("position") or {}).get("abbreviation"),
        "experience": (athlete.get("experience") or {}).get("years", 0),
        "image_url": (athlete.get("headshot") or {}).get("href", ""),
        "college": college.get("name"),
        "college_espn_id": college.get("id"),
        "college_aliases": sorted(a for a in aliases if a),
        "college_mascot": college.get("mascot"),
        "college_colors": " and ".join(color_names) or None,
        "college_colors_hex": college_info.get("colors_hex", []),
        "college_conference": conference,
        "college_logo": ((college.get("logos") or [{}])[0]).get("href"),
        "updated_at": datetime.now(),
    }


def sync_players(leagues: Optional[list] = None, log=print) -> int:
    """Fetch rosters from ESPN and upsert players. Returns players written."""
    leagues = leagues or list(LEAGUES)

    with ThreadPoolExecutor(max_workers=16) as pool:
        jobs = []
        for league in leagues:
            team_ids = fetch_team_ids(league)
            log(f"{league}: fetching {len(team_ids)} rosters")
            jobs += [(league, pool.submit(fetch_roster, league, tid)) for tid in team_ids]

        athletes = [
            (league, a)
            for league, job in jobs
            for a in job.result()
            if (a.get("college") or {}).get("id")
        ]

        college_ids = sorted({a["college"]["id"] for _, a in athletes})
        log(f"Fetching details for {len(college_ids)} colleges")
        colleges = dict(zip(college_ids, pool.map(fetch_college, college_ids)))

    players = [_build_player(a, league, colleges[a["college"]["id"]]) for league, a in athletes]
    if not players:
        raise Exception("ESPN returned no players; check network access")

    coll = get_players_collection()
    coll.bulk_write([
        UpdateOne({"espn_id": p["espn_id"]}, {"$set": p}, upsert=True) for p in players
    ])
    coll.create_index("espn_id", unique=True, sparse=True)
    coll.create_index([("league", 1), ("experience", 1)])

    # Drop hand-seeded sample players now that real data is available
    removed = coll.delete_many({"source": {"$ne": "espn"}}).deleted_count
    log(f"Synced {len(players)} players from ESPN (removed {removed} sample players)")
    return len(players)


def needs_sync() -> bool:
    """True when there is no ESPN data yet or it is older than SYNC_MAX_AGE."""
    newest = get_players_collection().find_one(
        {"source": "espn"}, sort=[("updated_at", -1)], projection={"updated_at": 1}
    )
    return not newest or datetime.now() - newest["updated_at"] > SYNC_MAX_AGE
