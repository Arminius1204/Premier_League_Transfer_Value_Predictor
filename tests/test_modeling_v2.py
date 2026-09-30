import pandas as pd
import numpy as np
import pytest
from pathlib import Path

DATA_DIR = Path("data/processed")

@pytest.fixture
def results():
    return pd.read_csv(DATA_DIR / "model_walk_forward_results_v2.csv")

def test_no_train_test_overlap(results):
    for idx, row in results.iterrows():
        train_seasons = set(row["train_seasons"].split(" + "))
        val_season = row["validation_season"]
        assert val_season not in train_seasons, f"Overlap in experiment {row['experiment_id']}"

def test_non_negative_predictions(results):
    assert (results["MAE"] >= 0).all(), "MAE must be non-negative"
    assert (results["RMSE"] >= 0).all(), "RMSE must be non-negative"

def test_baseline_predictions_present(results):
    baselines = ["Mean_Baseline", "Median_Baseline", "Pos_Median_Baseline"]
    models_run = results["model"].unique()
    for b in baselines:
        assert b in models_run, f"{b} missing"

def test_holdout_isolation(results):
    exp5 = results[results["experiment_id"] == 5]
    assert len(exp5) > 0
    assert (exp5["validation_season"] == "2023_2024").all(), "Holdout must be 2023/24"
    assert ("2023_2024" not in exp5.iloc[0]["train_seasons"]), "2023/24 leaked into training"
