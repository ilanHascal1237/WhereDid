"""Tests for the pure/near-pure business logic in app.services.

These exercise `_normalize`, `_answer_forms`, `difficulty_rules`,
`public_player` and `public_college` directly -- none of them touch
MongoDB, so no live DB connection is required to run this file.
"""
import pytest

from app.services import (
    DIFFICULTIES,
    _answer_forms,
    _normalize,
    difficulty_rules,
    public_college,
    public_player,
)


# ---------------------------------------------------------------------------
# _normalize
# ---------------------------------------------------------------------------

class TestNormalize:
    def test_strips_filler_words_and_matches_bare_name(self):
        assert _normalize("University of Michigan") == _normalize("Michigan")
        assert _normalize("University of Michigan") == "michigan"

    def test_drops_the_and_college(self):
        assert _normalize("The Ohio State University") == "ohio state"
        assert _normalize("Boston College") == "boston"

    def test_ampersand_becomes_and(self):
        # '&' is expanded to the word 'and' before punctuation stripping.
        assert "and" in _normalize("Texas A&M").split()
        assert "&" not in _normalize("Texas A&M")

    def test_punctuation_is_stripped(self):
        assert _normalize("Miami (FL)") == "miami fl"
        # apostrophes/periods are stripped entirely, not replaced with spaces
        assert _normalize("St. John's") == "st johns"

    def test_is_case_insensitive(self):
        assert _normalize("MICHIGAN") == _normalize("michigan") == "michigan"

    def test_collapses_whitespace(self):
        assert _normalize("  Duke   University  ") == "duke"

    def test_handles_none_and_empty(self):
        assert _normalize(None) == ""
        assert _normalize("") == ""
        assert _normalize("   ") == ""


# ---------------------------------------------------------------------------
# _answer_forms
# ---------------------------------------------------------------------------

class TestAnswerForms:
    def test_includes_normalized_college_name(self):
        player = {"college": "Duke University", "college_aliases": []}
        assert "duke" in _answer_forms(player)

    def test_includes_aliases(self):
        player = {"college": "Duke University", "college_aliases": ["Blue Devils"]}
        forms = _answer_forms(player)
        assert "duke" in forms
        assert "blue devils" in forms

    def test_miami_fl_also_accepts_bare_miami(self):
        player = {"college": "Miami (FL)", "college_aliases": []}
        forms = _answer_forms(player)
        assert "miami fl" in forms
        assert "miami" in forms

    def test_missing_aliases_key_is_tolerated(self):
        # college_aliases absent entirely (not just empty) should not raise
        player = {"college": "Clemson"}
        assert _answer_forms(player) == {"clemson"}

    def test_none_and_blank_names_are_skipped(self):
        player = {"college": "Clemson", "college_aliases": [None, "", "Tigers"]}
        forms = _answer_forms(player)
        assert forms == {"clemson", "tigers"}
        assert "" not in forms

    def test_no_college_at_all_yields_empty_set(self):
        player = {"college": None, "college_aliases": []}
        assert _answer_forms(player) == set()


# ---------------------------------------------------------------------------
# difficulty_rules
# ---------------------------------------------------------------------------

class TestDifficultyRules:
    @pytest.mark.parametrize("level", ["easy", "medium", "hard"])
    def test_returns_matching_rules_for_known_levels(self, level):
        assert difficulty_rules(level) == DIFFICULTIES[level]

    def test_unknown_difficulty_falls_back_to_medium(self):
        assert difficulty_rules("nightmare") == DIFFICULTIES["medium"]

    def test_empty_or_none_falls_back_to_medium(self):
        assert difficulty_rules("") == DIFFICULTIES["medium"]
        assert difficulty_rules(None) == DIFFICULTIES["medium"]


# ---------------------------------------------------------------------------
# public_player
# ---------------------------------------------------------------------------

class TestPublicPlayer:
    PLAYER = {
        "_id": "abc123",
        "name": "Jordan Example",
        "league": "NBA",
        "image_url": "http://img/example.png",
        "college": "Duke",
        "college_logo": "http://img/duke.png",
    }

    def test_hides_college_fields_when_not_revealed(self):
        payload = public_player(self.PLAYER, reveal=False)
        assert "college" not in payload
        assert "collegeLogo" not in payload

    def test_includes_college_fields_when_revealed(self):
        payload = public_player(self.PLAYER, reveal=True)
        assert payload["college"] == "Duke"
        assert payload["collegeLogo"] == "http://img/duke.png"

    def test_renames_fields_to_camel_case(self):
        payload = public_player(self.PLAYER, reveal=False)
        assert payload["id"] == "abc123"
        assert payload["name"] == "Jordan Example"
        assert payload["league"] == "NBA"
        assert payload["imageUrl"] == "http://img/example.png"
        # snake_case keys should not leak through
        assert "image_url" not in payload

    def test_id_is_stringified(self):
        class FakeObjectId:
            def __str__(self):
                return "mock-oid"

        player = {**self.PLAYER, "_id": FakeObjectId()}
        payload = public_player(player, reveal=False)
        assert payload["id"] == "mock-oid"

    def test_default_reveal_is_false(self):
        payload = public_player(self.PLAYER)
        assert "college" not in payload


# ---------------------------------------------------------------------------
# public_college
# ---------------------------------------------------------------------------

class TestPublicCollege:
    COLLEGE = {
        "_id": "espn-123",
        "mascot": "Blue Devils",
        "college": "Duke",
        "logo": "http://img/duke-logo.png",
    }

    def test_hides_college_and_logo_when_not_revealed(self):
        payload = public_college(self.COLLEGE, reveal=False)
        assert "college" not in payload
        assert "logo" not in payload
        assert payload == {"id": "espn-123", "mascot": "Blue Devils"}

    def test_includes_college_and_logo_when_revealed(self):
        payload = public_college(self.COLLEGE, reveal=True)
        assert payload["college"] == "Duke"
        assert payload["logo"] == "http://img/duke-logo.png"
        assert payload["id"] == "espn-123"
        assert payload["mascot"] == "Blue Devils"

    def test_default_reveal_is_false(self):
        payload = public_college(self.COLLEGE)
        assert "college" not in payload
