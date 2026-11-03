"""Tests for GameService.check_guess and MascotService.check_guess.

Both touch MongoDB (via `_find_player` / `_college_groups`), so these tests
patch `app.services.get_players_collection` with small in-memory fakes
instead of connecting to a real database. Kept intentionally minimal --
just enough to cover the matching logic, not a general mocking framework.
"""
from unittest.mock import patch

from bson.objectid import ObjectId

from app.services import GameService, MascotService


# ---------------------------------------------------------------------------
# GameService.check_guess
# ---------------------------------------------------------------------------

class _FakePlayersCollection:
    """Fake players collection supporting only find_one, as used by _find_player."""

    def __init__(self, players):
        self._players = {p["_id"]: p for p in players}

    def find_one(self, query):
        return self._players.get(query.get("_id"))


class TestGameServiceCheckGuess:
    def _player(self, **overrides):
        base = {
            "_id": ObjectId(),
            "name": "Jordan Example",
            "league": "NBA",
            "image_url": None,
            "college": "Duke",
            "college_aliases": [],
            "college_logo": None,
        }
        base.update(overrides)
        return base

    def test_correct_guess_returns_true_and_player(self):
        player = self._player()
        fake_collection = _FakePlayersCollection([player])
        with patch("app.services.get_players_collection", return_value=fake_collection):
            correct, returned = GameService.check_guess(str(player["_id"]), "Duke")
        assert correct is True
        assert returned is player

    def test_guess_matching_alias_or_normalized_form_is_correct(self):
        player = self._player(college="University of Michigan")
        fake_collection = _FakePlayersCollection([player])
        with patch("app.services.get_players_collection", return_value=fake_collection):
            correct, _ = GameService.check_guess(str(player["_id"]), "michigan")
        assert correct is True

    def test_wrong_guess_returns_false_but_still_returns_player(self):
        player = self._player()
        fake_collection = _FakePlayersCollection([player])
        with patch("app.services.get_players_collection", return_value=fake_collection):
            correct, returned = GameService.check_guess(str(player["_id"]), "UNC")
        assert correct is False
        assert returned is player

    def test_unknown_player_id_returns_false_none(self):
        fake_collection = _FakePlayersCollection([])
        with patch("app.services.get_players_collection", return_value=fake_collection):
            correct, returned = GameService.check_guess(str(ObjectId()), "Duke")
        assert (correct, returned) == (False, None)

    def test_malformed_player_id_returns_false_none(self):
        fake_collection = _FakePlayersCollection([])
        with patch("app.services.get_players_collection", return_value=fake_collection):
            correct, returned = GameService.check_guess("not-a-valid-object-id", "Duke")
        assert (correct, returned) == (False, None)


# ---------------------------------------------------------------------------
# MascotService.check_guess
# ---------------------------------------------------------------------------

class _FakeAggregateCollection:
    """Fake players collection supporting the aggregate() pipeline shape used
    by `_college_groups`: a single $match stage followed by a $group by
    college_espn_id. Good enough to exercise MascotService.check_guess
    without a real Mongo aggregation pipeline.
    """

    def __init__(self, player_docs):
        self._docs = player_docs

    def aggregate(self, pipeline):
        match = pipeline[0]["$match"]

        def matches(doc):
            for key, value in match.items():
                if key == "college_espn_id" and isinstance(value, dict) and "$ne" in value:
                    continue  # the "has an espn id at all" filter; all fakes satisfy it
                if doc.get(key) != value:
                    return False
            return True

        groups = {}
        for doc in self._docs:
            if not matches(doc):
                continue
            cid = doc["college_espn_id"]
            groups.setdefault(cid, {
                "_id": cid,
                "college": doc["college"],
                "college_aliases": doc.get("college_aliases"),
                "mascot": doc["college_mascot"],
                "colors": doc["college_colors"],
                "conference": doc["college_conference"],
                "logo": doc["college_logo"],
                "players": 0,
            })
            groups[cid]["players"] += 1
        return list(groups.values())


class TestMascotServiceCheckGuess:
    # Two different schools that share a mascot but differ on conference/colors.
    DOCS = [
        {
            "college_espn_id": "clemson",
            "college": "Clemson",
            "college_aliases": [],
            "college_mascot": "Tigers",
            "college_colors": "Orange",
            "college_conference": "ACC",
            "college_logo": "clemson.png",
        },
        {
            "college_espn_id": "auburn",
            "college": "Auburn",
            "college_aliases": [],
            "college_mascot": "Tigers",
            "college_colors": "Blue",
            "college_conference": "SEC",
            "college_logo": "auburn.png",
        },
    ]

    def test_exact_school_match_is_always_correct(self):
        fake_collection = _FakeAggregateCollection(self.DOCS)
        with patch("app.services.get_players_collection", return_value=fake_collection):
            correct, target = MascotService.check_guess("clemson", "Clemson", "easy")
        assert correct is True
        assert target["_id"] == "clemson"

    def test_hard_mode_accepts_any_school_sharing_the_mascot(self):
        # On hard mode no clues are shown, so any same-mascot school counts.
        # The target is "clemson" but the guess "Auburn" also has the Tigers
        # mascot, so it should be accepted -- and the matched school (Auburn)
        # is what gets returned, not the original target.
        fake_collection = _FakeAggregateCollection(self.DOCS)
        with patch("app.services.get_players_collection", return_value=fake_collection):
            correct, matched = MascotService.check_guess("clemson", "Auburn", "hard")
        assert correct is True
        assert matched["_id"] == "auburn"

    def test_easy_mode_rejects_same_mascot_school_with_different_clues(self):
        # Easy mode shows conference + colors, which differ between the two.
        fake_collection = _FakeAggregateCollection(self.DOCS)
        with patch("app.services.get_players_collection", return_value=fake_collection):
            correct, target = MascotService.check_guess("clemson", "Auburn", "easy")
        assert correct is False
        assert target["_id"] == "clemson"

    def test_unknown_college_id_returns_false_none(self):
        fake_collection = _FakeAggregateCollection(self.DOCS)
        with patch("app.services.get_players_collection", return_value=fake_collection):
            correct, target = MascotService.check_guess("nonexistent", "Clemson", "medium")
        assert (correct, target) == (False, None)
