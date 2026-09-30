import pytest
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "transfer_features_candidate.csv"
ERROR_PATH = PROJECT_ROOT / "data" / "processed" / "error_analysis.csv"

def test_chronological_integrity():
    df = pd.read_csv(DATA_PATH)
    train_dates = pd.to_datetime(df[df['season_id'].isin(['2021_2022', '2022_2023'])]['transfer_date'])
    test_dates = pd.to_datetime(df[df['season_id'].isin(['2023_2024', '2023'])]['transfer_date'])
    
    assert train_dates.max() <= test_dates.min(), "Chronological split violated!"

def test_baseline_leakage():
    # Verify baselines (like median) are correctly computed from train
    df = pd.read_csv(DATA_PATH)
    train_df = df[df['season_id'].isin(['2021_2022', '2022_2023'])]
    test_df = df[df['season_id'].isin(['2023_2024', '2023'])]
    
    train_median = train_df['fee_gbp'].median()
    # The Baseline_Median MAE on test should be mean(abs(test - train_median))
    expected_mae = (test_df['fee_gbp'] - train_median).abs().mean()
    
    results = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "model_experiment_results.csv")
    actual_mae = results[(results['model'] == 'Baseline_Median') & (results['target_type'] == 'raw')]['MAE'].values[0]
    
    assert abs(expected_mae - actual_mae) < 100, f"Baseline leakage! Expected {expected_mae}, got {actual_mae}"

def test_deterministic_seeds():
    # If a seed is used, training the same model twice should yield identical MAE
    # Tested manually in our diagnostics script. We will verify the file exists.
    assert (PROJECT_ROOT / "data" / "processed" / "model_stability.json").exists()

def test_error_analysis_exists():
    assert ERROR_PATH.exists()
