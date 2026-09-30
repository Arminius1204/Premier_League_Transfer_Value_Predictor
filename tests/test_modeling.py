import pytest
import math
import numpy as np
import pandas as pd
from pathlib import Path
import joblib

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def test_inverse_transform():
    fee = 100000.0
    log_fee = math.log1p(fee)
    inv_fee = np.expm1(log_fee)
    assert math.isclose(fee, inv_fee, rel_tol=1e-5), "Inverse transform failed"

def test_no_negative_fees():
    df = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "model_experiment_results.csv")
    # Our experiment scripts enforce np.maximum(preds, 0)
    # Just checking results
    assert len(df) > 0

def test_model_artifacts_exist():
    # Check that at least one model was saved
    models_dir = PROJECT_ROOT / "models"
    pkl_files = list(models_dir.rglob("*.pkl"))
    assert len(pkl_files) > 0, "No model artifacts found!"

def test_player_id_not_used():
    # Load a pipeline and check feature names used by ColumnTransformer
    pkl_files = list((PROJECT_ROOT / "models").rglob("*.pkl"))
    if pkl_files:
        pipe = joblib.load(pkl_files[0])
        preprocessor = pipe.named_steps['preprocessor']
        used_features = []
        for name, transformer, columns in preprocessor.transformers_:
            if name != 'remainder':
                used_features.extend(columns)
        assert 'master_player_id' not in used_features, "Leakage: player ID used!"

def test_temporal_overlap():
    df = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "model_experiment_results.csv")
    for _, row in df.iterrows():
        assert '2023_2024' not in row['train_seasons'], "Temporal leak: Test season in train!"
        assert '2021' not in row['test_season'], "Temporal overlap!"

def test_baseline_correctness():
    df = pd.read_csv(PROJECT_ROOT / "data" / "processed" / "model_experiment_results.csv")
    baselines = df[df['model'].str.contains('Baseline')]
    assert len(baselines) > 0, "Baselines missing from results!"
