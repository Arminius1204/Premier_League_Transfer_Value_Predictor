import pandas as pd
import numpy as np
import pytest
from pathlib import Path

DATA_DIR = Path("data/processed")

@pytest.fixture
def core_features():
    return pd.read_csv(DATA_DIR / "transfer_features_core_v2.csv")

@pytest.fixture
def enriched_features():
    return pd.read_csv(DATA_DIR / "transfer_features_enriched_v2.csv")

def test_six_season_coverage(core_features):
    seasons = core_features["season_id"].unique()
    expected = ["2018_2019", "2019_2020", "2020_2021", "2021_2022", "2022_2023", "2023_2024"]
    for s in expected:
        assert s in seasons, f"Missing season {s}"

def test_one_row_per_transfer(core_features):
    assert len(core_features) == len(core_features["transfer_id"].unique())

def test_valid_age(core_features):
    # Age should generally be between 15 and 45. Some might be missing.
    valid_ages = core_features["age_at_transfer"].dropna()
    assert (valid_ages >= 14).all(), "Found impossibly young player"
    assert (valid_ages <= 50).all(), "Found impossibly old player"

def test_valid_position_mapping(core_features):
    valid_positions = {"GOALKEEPER", "DEFENDER", "MIDFIELDER", "FORWARD", "UNKNOWN"}
    unique_pos = set(core_features["position"].unique())
    assert unique_pos.issubset(valid_positions), f"Invalid positions found: {unique_pos - valid_positions}"

def test_no_negative_minutes_or_goals(enriched_features):
    if "t1_minutes" in enriched_features.columns:
        assert (enriched_features["t1_minutes"].dropna() >= 0).all()
    if "t1_goals" in enriched_features.columns:
        assert (enriched_features["t1_goals"].dropna() >= 0).all()

def test_target_aliases_are_absent(core_features):
    forbidden = ["fee_numeric", "raw_fee_string", "original_fee"]
    for f in forbidden:
        assert f not in core_features.columns

def test_destination_club_is_absent(core_features):
    forbidden = ["to_club_id", "destination_club"]
    for f in forbidden:
        assert f not in core_features.columns

def test_log_fee_calculation(core_features):
    expected_log = np.log1p(core_features["fee_gbp"].replace(0, np.nan).dropna())
    actual_log = core_features["log_fee_gbp"][core_features["fee_gbp"] > 0]
    np.testing.assert_array_almost_equal(expected_log, actual_log)
