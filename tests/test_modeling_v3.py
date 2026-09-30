import pandas as pd
import pytest
import numpy as np
from pathlib import Path

DATA_DIR = Path("data/processed")

@pytest.fixture
def holdout():
    return pd.read_csv(DATA_DIR / "final_holdout_predictions_v3.csv")

def test_interval_bounds(holdout):
    # Ensure lower bound <= prediction <= upper bound
    assert (holdout["lower_bound_80"] <= holdout["predicted_fee"] + 0.01).all()
    assert (holdout["upper_bound_80"] >= holdout["predicted_fee"] - 0.01).all()

def test_no_negative_intervals(holdout):
    assert (holdout["lower_bound_80"] >= 0).all()
    assert (holdout["lower_bound_90"] >= 0).all()

def test_interval_coverage_logic(holdout):
    manual_coverage_80 = ((holdout["fee_gbp"] >= holdout["lower_bound_80"]) & 
                          (holdout["fee_gbp"] <= holdout["upper_bound_80"]))
    assert (manual_coverage_80 == holdout["covered_80"]).all()
    
def test_no_target_leakage_in_test_set(holdout):
    # final_holdout_predictions_v3 should only contain 2023_2024
    assert (holdout["season_id"] == "2023_2024").all(), "Holdout test set leaked multiple seasons!"
