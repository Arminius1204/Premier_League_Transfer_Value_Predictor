# Phase 13 Player Intelligence Engine Report

## 1. Executive Summary
Phase 13 successfully wrapped the frozen Phase 12 Machine Learning core into an interactive Player Intelligence Engine. This layer empowers analysts and scouts to search for historically comparable players via the **Similarity Engine** and perturb player profiles to map valuation boundaries via the **What-If Valuation Simulator**. 

Absolutely no Phase 12 models, weights, preprocessing schemas, or uncertainty logic were retrained or modified, strictly honoring the read-only integrity of `models/v3/`. 

## 2. Phase 12 Integration Audit
A rigorous pre-implementation audit verified:
*   **Production Estimator:** Weighted Ensemble (`Ridge`, `XGBoost`, `RandomForest`).
*   **Frozen Artifact:** `models/v3/ensemble/ensemble_metadata.joblib` and base models.
*   **Preprocessing:** `final_preprocessor.joblib`. Median imputation for numerical, one-hot for categorical `position`. Seven sparse variables (e.g. `age_at_transfer` for earlier historical years lacking demographic matches) were properly logged by the imputer as dropped. 
*   **Uncertainty:** Empirical conformal prediction margins (`q_80`, `q_90`) retrieved directly from Phase 12.

## 3. Player Similarity Engine
The Similarity Engine is designed to identify players with analogous performance profiles.
*   **Methodology:** Cosine Similarity applied to standardized numerical vectors. 
*   **Features:** Evaluates `t1_minutes`, `t1_goals_per90`, `t1_assists_per90`, `t1_bps_per90`, `career_minutes_before_transfer`, `selling_club_pts_t1`. 
*   **Exclusions:** `fee_gbp` and identity markers (`master_player_id`) are explicitly excluded so that price does not distort performance-based similarity.
*   **Position Handling:** Strict filtration guarantees that defenders are exclusively mapped against defenders. 
*   **Missing-Data:** Isolated standard scalers and median imputers were built internally (by position) to prevent `NaN` values from skewing the cosine similarity distance. Missing data coverage is returned to the user alongside the score.

## 4. What-If Valuation Simulator
The Simulator pushes hypothetical feature dictionaries precisely through the frozen production ML pipeline.
*   **Baseline Validation:** A strict baseline reproduction check ensures that passing a historical player's unperturbed profile into the Simulator exactly replicates the £-value point estimate and absolute error boundaries generated independently during Phase 12.
*   **Scenario Validation:** Users can specify deltas (e.g., `{'t1_goals_per90': 0.85}`). The simulator returns `Baseline Prediction`, `Scenario Prediction`, `Absolute Change`, `Percentage Change`, and conformal bounds.
*   **Uncertainty Integration:** Phase 12 historical conformal brackets natively encompass the new Scenario Predictions, retaining negative-price clipping rules (`min £0`).
*   **Out-of-Distribution (OOD) Detection:** The simulator scans the proposed scenario against the global historical `Min`/`Max` training bounds for every input. If an analyst proposes `Goals/90 = 2.5`, the system attaches an explicit OOD warning indicating the model is extrapolating dangerously.

## 5. Testing
The test suite enforces mathematical rigor across the newly built engines while heavily defending Phase 12 regression:
*   `Existing tests:` 38 passed
*   `Phase 13 tests:` 12 passed
*   `Total:` 50 passed

Tests strictly assert that bounds are non-negative, `fee_gbp` is purged from similarity vectors, and OOD triggers flag violations accurately.

## 6. Architecture & File Registry
**Files Created:**
*   `ml/similarity/engine.py` (Similarity Engine)
*   `ml/prediction/what_if.py` (What-If Simulator)
*   `tests/test_phase13.py` (50 combined assertions)
*   `docs/phase13_pre_implementation_audit.md` (Integrity mapping)
*   `docs/phase13_similarity_engine.md` (Engine design)
*   `docs/phase13_what_if_simulator.md` (Simulator design)
*   `docs/phase13_player_intelligence_report.md` (This document)

**Files Modified:**
*   None. Phase 12 artifacts remained fundamentally isolated and unwritten.

## 7. Integrity & Limitations
**Phase 12 Integrity:** No Phase 12 artifacts were modified, refit, or overwritten. 
**Limitations:**
1.  **Missing FPL Demographics:** `age_at_transfer` remains 100% missing in our historical data pipeline owing to the FPL-to-Transfermarkt linkage limitation mapping historical DOBs. The ML model robustly ignores it via the preprocessor, but it reduces the granularity of demographic similarity. 
2.  **Dataset Position Sparsity:** Historical position data from the current Phase 10 linkage mapped largely to `UNKNOWN`, meaning the Similarity Engine operates globally in practice until position linkage is enhanced in the ETL phase. 
3.  **Non-Causal Interpretability:** As designed, this module cannot ascertain that scoring more goals *causes* a price hike; it purely models historical price sensitivity.

## 8. Recommendation
The Player Intelligence modules (Similarity + What-If) are functionally complete and fully wrapped over the production-ready ML Core. 

**Next Phase Recommendation:** **Phase 14 — Interactive FastAPI & Next.js Dashboard.** The system possesses a powerful predictive backend; it now requires a unified, web-accessible interface to allow users to interact dynamically with the Similarity arrays and What-If forms.
