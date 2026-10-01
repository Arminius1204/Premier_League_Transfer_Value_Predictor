import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_get_players_search():
    response = client.get("/players?q=Bruno&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) <= 5

def test_get_player_detail_unknown():
    response = client.get("/players/unknown_id")
    assert response.status_code == 404

def test_get_player_detail_known():
    # Let's get a real player from search first
    search_response = client.get("/players?limit=1")
    player_id = search_response.json()["items"][0]["master_player_id"]
    
    response = client.get(f"/players/{player_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["master_player_id"] == player_id
    assert "transfer_history" in data

def test_player_valuation():
    search_response = client.get("/players?limit=1")
    player_id = search_response.json()["items"][0]["master_player_id"]
    
    response = client.get(f"/players/{player_id}/valuation")
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "lower_bound" in data
    assert "upper_bound" in data
    assert data["lower_bound"] <= data["prediction"] <= data["upper_bound"]
    
def test_player_explanation():
    search_response = client.get("/players?limit=1")
    player_id = search_response.json()["items"][0]["master_player_id"]
    
    response = client.get(f"/players/{player_id}/explanation")
    assert response.status_code == 200
    data = response.json()
    assert "positive_contributors" in data
    assert "negative_contributors" in data

def test_player_similarity():
    search_response = client.get("/players?limit=1")
    player_id = search_response.json()["items"][0]["master_player_id"]
    
    response = client.get(f"/players/{player_id}")
    season = response.json()["seasons"][-1]
    
    response = client.get(f"/players/{player_id}/similar?season={season}&top_k=5")
    # May return 422 if insufficient coverage; both are acceptable outcomes
    assert response.status_code in [200, 422]
    if response.status_code == 200:
        data = response.json()
        assert "results" in data

def test_profile_similarity():
    # Find a valid position from the data
    search_response = client.get("/players?limit=1")
    detail_response = client.get(f"/players/{search_response.json()['items'][0]['master_player_id']}")
    pos = detail_response.json().get("position", "UNKNOWN")
    
    payload = {
        "position": pos if pos else "UNKNOWN",
        "age_at_transfer": 22,
        "t1_minutes": 2100,
        "t1_goals_per90": 0.55,
        "t1_assists_per90": 0.21,
        "t1_bps_per90": 6.2,
        "career_minutes_before_transfer": 6000,
        "selling_club_pts_t1": 61
    }
    response = client.post("/similarity/profile", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data

def test_what_if_simulation():
    search_response = client.get("/players?limit=1")
    player_id = search_response.json()["items"][0]["master_player_id"]
    
    player_detail = client.get(f"/players/{player_id}").json()
    season = player_detail["seasons"][-1]
    
    payload = {
        "player_id": player_id,
        "season": season,
        "changes": {
            "t1_goals_per90": 0.85
        }
    }
    response = client.post("/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "baseline" in data
    assert "scenario" in data
    assert "warnings" in data
    assert data["changed_features"]["t1_goals_per90"] == 0.85

def test_transfers():
    response = client.get("/transfers?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) <= 5

def test_market_analysis():
    response = client.get("/market-analysis")
    assert response.status_code == 200
    data = response.json()
    assert "total_transfers" in data
    assert "median_fee" in data

def test_model_metadata():
    response = client.get("/models")
    assert response.status_code == 200
    data = response.json()
    assert data["production_model"] == "weighted_ensemble"
    assert "metrics" in data
