# Phase 13 Pre-Implementation Audit

## 1. Objective
Before building the Player Similarity Engine and What-If Valuation Simulator, this audit verifies the exact architecture of the frozen Phase 12 valuation models to ensure zero regression and exact baseline replication.

## 2. Frozen Production Architecture
*   **Artifact Location:** `models/v3/`
*   **Production Estimator:** Weighted Ensemble containing `Ridge`, `XGBoost`, and `RandomForest`.
*   **Ensemble Weights:** 
    *   Ridge: 33.48%
    *   XGBoost: 33.39%
    *   Random Forest: 33.13%
*   **Uncertainty Methodology:** Conformal Prediction using historical out-of-fold absolute residuals.
    *   `q_80` (80% Interval): ± £12,949,835
    *   `q_90` (90% Interval): ± £21,433,656

## 3. Preprocessing Pipeline (`preprocessors/final_preprocessor.joblib`)
*   **Numeric Features (21):** `age_at_transfer`, `age_squared`, `previous_transfer_count`, `career_minutes_before_transfer`, `career_goals_before_transfer`, `selling_club_pts_t1`, `selling_club_gd_t1`, `transfer_month`, `is_summer_window`, `t1_minutes`, `t1_goals`, `t1_assists`, `t1_bps`, `t1_goals_per90`, `t1_assists_per90`, `t1_bps_per90`, `t1_low_minutes_flag`, `two_season_avg_minutes`, `two_season_avg_goals`, `goals_trend`, `previous_transfer_fee_gbp`
    *   *Handling:* `SimpleImputer(strategy='median')` -> `StandardScaler()`
*   **Categorical Features (1):** `position`
    *   *Handling:* `SimpleImputer(strategy='constant', fill_value='UNKNOWN')` -> `OneHotEncoder(handle_unknown='ignore')`
*   **Target Output:** `fee_gbp` (Raw Fee in GBP. Log models were discarded). Negative predictions are clipped at `0`.

## 4. Integration Risks & Rules
*   **Baseline Strictness:** The What-If Simulator must pipe feature inputs explicitly through the loaded `final_preprocessor.joblib` and the three base estimators, then compute the weighted average and clip to 0. It must exactly match Phase 12's outputs.
*   **Read-Only Guarantee:** The simulator will only `joblib.load()`. No `.fit()` methods will be called in Phase 13.
*   **Similarity Separation:** The Similarity Engine needs a conceptually separate scaling and imputation logic from the ML model since it focuses on nearest-neighbor distance (Cosine Similarity) over predictive modeling. We will instantiate a new standard scaler just for similarity.
*   **Blocked Datasets:** Capology, Understat, FBref remain blocked/missing. Similarity will rely heavily on FPL `bps_per90` and `goals_per90` alongside historical demographics.

**Audit Status:** Complete. No blocking defects found. Phase 12 artifacts are valid and intact.
