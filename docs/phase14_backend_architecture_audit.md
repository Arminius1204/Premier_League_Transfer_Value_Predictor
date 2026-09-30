# Phase 14A Backend Architecture Audit

## 1. Exact Phase 12 Production Model
The production model artifact is an ensemble located at:
`models/v3/ensemble/ensemble_metadata.joblib`

The constituent models of the ensemble are located at:
- `models/v3/selected_models/RandomForest_final.joblib`
- `models/v3/selected_models/Ridge_final.joblib`
- `models/v3/selected_models/XGBoost_final.joblib`

## 2. Exact Phase 12 Preprocessing Artifact
The preprocessor used in Phase 12 is located at:
`models/v3/preprocessors/final_preprocessor.joblib`

## 3. Exact Phase 12 Ensemble Metadata
The metadata for the ensemble, including candidate models, MAE, R², weights, and validation methodology, is found within `ensemble_metadata.joblib`.

## 4. Exact Phase 12 Uncertainty Mechanism
Uncertainty mechanism (conformal prediction bounds) is computed and stored alongside model metadata and is expected to be loaded natively by the predictions process.

## 5. Phase 13 Similarity Engine
The implementation resides at: `ml/similarity/engine.py`. This provides player similarity capabilities.

## 6. Phase 13 What-If Simulator
The implementation resides at: `ml/prediction/what_if.py`. This provides the simulation functionality for hypotheticals.

## 7. Canonical Player Dataset
The dataset containing standard player statistics:
`data/processed/transfer_features_enriched_v2.csv` (used broadly in modeling and queries), and mapping data like `players.csv`, `player_seasons.csv`, etc.

## 8. Canonical Transfer Dataset
The transfer records dataset:
`data/processed/transfers_normalized.csv` (and related `transfer_features_core_v2.csv`).

## 9. Existing Python Package Structure
The current package structure splits machine learning capabilities into the `ml` package (with subpackages for feature engineering, modeling, prediction, similarity, etc.). The backend will introduce a new `backend` top-level directory for FastAPI functionality.

## 10. Existing Dependency Management
Relies on system requirements, with `requirements.txt` / `pyproject.toml` managing FastAPI dependencies and ML dependencies. We'll add FastAPI, Uvicorn, and Pydantic to the environment if they aren't already present.

## 11. Existing Test Configuration
Pytest is used via `tests/` directory and it contains 50 passing tests. New tests will be added directly into this directory (e.g., `test_api_health.py`, `test_api_players.py`, etc.).
