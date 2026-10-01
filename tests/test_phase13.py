import pandas as pd
import numpy as np
import pytest
from pathlib import Path
from ml.similarity.engine import PlayerSimilarityEngine
from ml.prediction.what_if import WhatIfSimulator

DATA_DIR = Path("data/processed")
MODELS_DIR = Path("models/v3")
DATA_FILE = DATA_DIR / "transfer_features_enriched_v2.csv"

@pytest.fixture(scope="module")
def sim_engine():
    return PlayerSimilarityEngine(DATA_FILE)

@pytest.fixture(scope="module")
def whatif_sim():
    return WhatIfSimulator(DATA_FILE, MODELS_DIR)

# --- SIMILARITY TESTS ---

def test_similarity_excludes_transfer_fee(sim_engine):
    assert "fee_gbp" not in sim_engine.sim_features
    assert "log_fee_gbp" not in sim_engine.sim_features

def test_similarity_excludes_player_id(sim_engine):
    assert "master_player_id" not in sim_engine.sim_features
    assert "transfer_id" not in sim_engine.sim_features

def test_self_similarity_is_max(sim_engine):
    p = sim_engine.df.iloc[0]
    score = sim_engine.compare_players(p["master_player_id"], p["season_id"], p["master_player_id"], p["season_id"])
    assert np.isclose(score, 1.0)

def test_similarity_is_bounded(sim_engine):
    p1 = sim_engine.df.iloc[0]
    pos = p1["position"]
    p2 = sim_engine.df[sim_engine.df["position"] == pos].iloc[1]
    score = sim_engine.compare_players(p1["master_player_id"], p1["season_id"], p2["master_player_id"], p2["season_id"])
    assert -1.0 <= score <= 1.0

def test_position_compatibility(sim_engine):
    # Mock positions for test — compare_players reads from self.df
    p1_idx = sim_engine.df.index[0]
    p2_idx = sim_engine.df.index[1]
    
    orig_pos1 = sim_engine.df.at[p1_idx, "position"]
    orig_pos2 = sim_engine.df.at[p2_idx, "position"]
    
    sim_engine.df.at[p1_idx, "position"] = "FWD"
    sim_engine.df.at[p2_idx, "position"] = "DEF"
    
    score = sim_engine.compare_players(
        sim_engine.df.iloc[0]["master_player_id"], sim_engine.df.iloc[0]["season_id"],
        sim_engine.df.iloc[1]["master_player_id"], sim_engine.df.iloc[1]["season_id"]
    )
    
    # Restore
    sim_engine.df.at[p1_idx, "position"] = orig_pos1
    sim_engine.df.at[p2_idx, "position"] = orig_pos2
    
    assert score == 0.0

def test_top_k_sorting(sim_engine):
    # Pick a player with sufficient feature coverage (>= 40%)
    adequate = sim_engine.df[sim_engine._row_coverage >= 0.4]
    if adequate.empty:
        pytest.skip("No player with adequate coverage for top-k test.")
    p = adequate.iloc[0]
    res = sim_engine.find_similar_players(p["master_player_id"], p["season_id"], top_k=3)
    scores = [r["Similarity Score"] for r in res]
    assert sorted(scores, reverse=True) == scores

def test_hypothetical_profile(sim_engine):
    # Provide enough features (>= 40% = 3/7) and a valid position from the dataset
    pos = sim_engine.df["position"].iloc[0]  # use actual position from data
    prof = {
        "position": pos,
        "age_at_transfer": 22,
        "t1_goals_per90": 0.5,
        "t1_minutes": 1800,
    }
    res = sim_engine.compare_profile_to_dataset(prof, top_k=2)
    assert len(res) == 2
    assert "Hypothetical Profile" in res[0]["Queried Player"]

# --- WHAT-IF TESTS ---

def test_baseline_matches_frozen_production(whatif_sim):
    # Load frozen predictions
    frozen = pd.read_csv(DATA_DIR / "final_holdout_predictions_v3.csv")
    test_row = frozen.iloc[0]
    
    # Query via whatif baseline
    res = whatif_sim.simulate(test_row["master_player_id"], test_row["season_id"], {})
    
    # Assert exact match
    assert np.isclose(res["Baseline Prediction"], test_row["predicted_fee"])
    assert np.isclose(res["Baseline Interval (80%)"][0], test_row["lower_bound_80"])
    assert np.isclose(res["Baseline Interval (80%)"][1], test_row["upper_bound_80"])

def test_scenario_modifies_prediction(whatif_sim):
    p = whatif_sim.df.iloc[0]
    # massive goals increase
    res = whatif_sim.simulate(p["master_player_id"], p["season_id"], {"t1_goals_per90": 2.5})
    assert res["Absolute Change"] != 0.0
    assert "t1_goals_per90" in res["Changed Features"]

def test_ood_warning(whatif_sim):
    p = whatif_sim.df.iloc[0]
    # Use a value within hard bounds [0, 5.0] but outside historical range
    extreme = 4.9
    res = whatif_sim.simulate(p["master_player_id"], p["season_id"], {"t1_goals_per90": extreme})
    assert res["ood"] is True
    assert "t1_goals_per90" in res["ood_features"]
    assert len(res["OOD Warnings"]) > 0

def test_in_distribution_no_warning(whatif_sim):
    p = whatif_sim.df.iloc[0]
    # median goals should be safe
    safe_goals = whatif_sim.df["t1_goals_per90"].median()
    res = whatif_sim.simulate(p["master_player_id"], p["season_id"], {"t1_goals_per90": safe_goals})
    assert len(res["OOD Warnings"]) == 0

def test_negative_price_handling(whatif_sim):
    p = whatif_sim.df.iloc[0]
    # Force awful stats to test 0 clipping
    res = whatif_sim.simulate(p["master_player_id"], p["season_id"], {"age_at_transfer": 45, "t1_minutes": 0, "career_minutes_before_transfer": 0})
    assert res["Scenario Prediction"] >= 0.0
    assert res["Scenario Interval (80%)"][0] >= 0.0
