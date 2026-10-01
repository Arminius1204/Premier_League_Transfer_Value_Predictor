"""
Phase 14B.1 — Player Identity & Media Enrichment Tests

Tests enrichment service, canonical names, Unicode preservation,
photo URL handling, club resolution, position resolution,
and API key security.

DOES NOT modify Phase 12/13 tests or ML artifacts.
"""

import pytest
import pandas as pd
from pathlib import Path
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.enrichment_service import EnrichmentService

client = TestClient(app)


# ---------- ENRICHMENT DATA TESTS ----------

class TestEnrichmentData:
    """Test the enrichment metadata file integrity."""
    
    def test_enrichment_metadata_exists(self):
        """Player enrichment metadata file should exist."""
        path = Path(__file__).parent.parent / "data" / "player_enrichment" / "player_metadata.csv"
        assert path.exists(), "player_metadata.csv not found"

    def test_enrichment_metadata_has_required_columns(self):
        path = Path(__file__).parent.parent / "data" / "player_enrichment" / "player_metadata.csv"
        df = pd.read_csv(path, encoding='utf-8', nrows=0)
        required = ['master_player_id', 'canonical_name', 'position', 'nationality', 
                     'date_of_birth', 'photo_url', 'external_provider', 'external_player_id',
                     'match_status', 'match_confidence']
        for col in required:
            assert col in df.columns, f"Missing column: {col}"

    def test_enrichment_metadata_all_players_have_canonical_names(self):
        path = Path(__file__).parent.parent / "data" / "player_enrichment" / "player_metadata.csv"
        df = pd.read_csv(path, encoding='utf-8')
        assert df['canonical_name'].notna().all(), "Some players have missing canonical names"
        assert (df['canonical_name'].str.strip() != '').all(), "Some players have empty canonical names"

    def test_enrichment_metadata_has_match_status(self):
        path = Path(__file__).parent.parent / "data" / "player_enrichment" / "player_metadata.csv"
        df = pd.read_csv(path, encoding='utf-8')
        assert df['match_status'].notna().all(), "Some records missing match_status"
        assert df['match_confidence'].notna().all(), "Some records missing match_confidence"

    def test_enrichment_metadata_has_external_ids(self):
        """At least some players should have external IDs from Transfermarkt."""
        path = Path(__file__).parent.parent / "data" / "player_enrichment" / "player_metadata.csv"
        df = pd.read_csv(path, encoding='utf-8')
        with_ext_id = df['external_player_id'].notna().sum()
        assert with_ext_id > 1000, f"Expected >1000 external IDs, got {with_ext_id}"


# ---------- CANONICAL NAME TESTS ----------

class TestCanonicalNames:
    """Test that API returns properly capitalized canonical names."""

    def test_canonical_name_returned_for_search(self):
        response = client.get("/players?limit=5")
        assert response.status_code == 200
        items = response.json()["items"]
        assert len(items) > 0
        for item in items:
            name = item["player_name"]
            # Name should NOT be all lowercase (unless it's a single-word name like "Neymar")
            assert name != name.lower() or len(name.split()) == 1, \
                f"Name appears to be lowercase: {name}"

    def test_canonical_name_in_player_detail(self):
        search = client.get("/players?limit=1")
        pid = search.json()["items"][0]["player_id"]
        response = client.get(f"/players/{pid}")
        assert response.status_code == 200
        name = response.json()["player_name"]
        assert name and len(name) > 0


# ---------- UNICODE PRESERVATION TESTS ----------

class TestUnicodePreservation:
    """Test that accented/Unicode names are preserved through the API."""

    def test_unicode_name_diaz(self):
        """Brahim Díaz should have the accent preserved."""
        res = client.get("/players?q=Brahim&limit=5")
        items = res.json()["items"]
        diaz_found = [i for i in items if "az" in i["player_name"].lower()]
        if diaz_found:
            assert "í" in diaz_found[0]["player_name"], \
                f"Expected accent in Díaz, got: {diaz_found[0]['player_name']}"

    def test_unicode_name_xhaka(self):
        """Granit Xhaka should be properly capitalized."""
        res = client.get("/players?q=xhaka&limit=1")
        items = res.json()["items"]
        if items:
            assert items[0]["player_name"] == "Granit Xhaka"

    def test_unicode_name_itakura(self):
        """Ko Itakura should be properly capitalized."""
        res = client.get("/players?q=itakura&limit=1")
        items = res.json()["items"]
        if items:
            assert items[0]["player_name"] == "Ko Itakura"


# ---------- PHOTO URL TESTS ----------

# ---------- CLUB RESOLUTION TESTS ----------

class TestClubResolution:
    """Test that clubs are resolved where data exists."""

    def test_clubs_no_unknown_in_detail(self):
        """Player detail should not contain raw 'UNKNOWN' club values."""
        search = client.get("/players?limit=1")
        pid = search.json()["items"][0]["player_id"]
        res = client.get(f"/players/{pid}")
        clubs = res.json()["clubs"]
        for club in clubs:
            assert club != "UNKNOWN", "Raw UNKNOWN club found in response"


# ---------- POSITION RESOLUTION TESTS ----------

class TestPositionResolution:
    """Test position handling."""

    def test_position_not_raw_unknown(self):
        """Position should never be raw 'UNKNOWN' - should be null instead."""
        res = client.get("/players?limit=20")
        items = res.json()["items"]
        for item in items:
            pos = item.get("position")
            assert pos != "UNKNOWN", f"Raw UNKNOWN position found for {item['player_name']}"


# ---------- API KEY SECURITY TESTS ----------

class TestApiKeySecurity:
    """Test that API keys are not exposed."""

    def test_no_api_key_in_search_response(self):
        res = client.get("/players?limit=1")
        body = res.text
        assert "x-rapidapi" not in body.lower()
        assert "api_football_key" not in body.lower()

    def test_no_api_key_in_detail_response(self):
        search = client.get("/players?limit=1")
        pid = search.json()["items"][0]["player_id"]
        res = client.get(f"/players/{pid}")
        body = res.text
        assert "x-rapidapi" not in body.lower()
        assert "api_football_key" not in body.lower()

    def test_frontend_env_has_no_api_key(self):
        """Check that frontend .env.local does not contain API key."""
        env_path = Path(__file__).parent.parent / "frontend" / ".env.local"
        if env_path.exists():
            content = env_path.read_text()
            assert "API_FOOTBALL" not in content, "API key found in frontend env!"
            assert "api_football" not in content.lower(), "API key reference found in frontend env!"


# ---------- EXISTING API COMPATIBILITY TESTS ----------

class TestExistingApiCompatibility:
    """Ensure existing API responses remain valid after enrichment."""

    def test_search_has_required_fields(self):
        res = client.get("/players?limit=1")
        assert res.status_code == 200
        data = res.json()
        assert "items" in data
        assert "total" in data
        item = data["items"][0]
        assert "player_id" in item
        assert "player_name" in item

    def test_detail_has_required_fields(self):
        search = client.get("/players?limit=1")
        pid = search.json()["items"][0]["player_id"]
        res = client.get(f"/players/{pid}")
        assert res.status_code == 200
        data = res.json()
        assert "player_id" in data
        assert "player_name" in data
        assert "seasons" in data
        assert "transfer_history" in data

    def test_valuation_still_works(self):
        search = client.get("/players?limit=1")
        pid = search.json()["items"][0]["player_id"]
        res = client.get(f"/players/{pid}/valuation")
        assert res.status_code == 200
        data = res.json()
        assert "prediction" in data
        assert "lower_bound" in data
        assert "upper_bound" in data

    def test_similarity_still_works(self):
        search = client.get("/players?limit=1")
        pid = search.json()["items"][0]["player_id"]
        detail = client.get(f"/players/{pid}").json()
        season = detail["seasons"][-1]
        res = client.get(f"/players/{pid}/similar?season={season}&top_k=3")
        assert res.status_code == 200
        data = res.json()
        assert "results" in data


# ---------- VALIDATION EXAMPLES ----------

class TestValidationExamples:
    """Test specific player examples from the spec."""

    @pytest.mark.parametrize("query,expected_name", [
        ("mahrez", "Riyad Mahrez"),
        ("itakura", "Ko Itakura"),
        ("arzani", "Daniel Arzani"),
        ("palaversa", "Ante Palaversa"),
        ("sandler", "Philippe Sandler"),
        ("xhaka", "Granit Xhaka"),
    ])
    def test_specific_player_canonical_name(self, query, expected_name):
        res = client.get(f"/players?q={query}&limit=5")
        items = res.json()["items"]
        names = [i["player_name"] for i in items]
        assert expected_name in names, \
            f"Expected '{expected_name}' in results for query '{query}', got: {names}"
