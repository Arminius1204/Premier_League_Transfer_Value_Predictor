# Phase 13 What-If Valuation Simulator

## 1. Architecture & Objective
The What-If Simulator allows users to perturb a player's historical statistics (e.g., "What if they had scored 0.5 Goals/90 instead of 0.2?") and observe how the market valuation responds.

It acts as a functional wrapper around the **Frozen Phase 12 ML Pipeline**. It loads the serialized `final_preprocessor.joblib`, the models (`Ridge`, `RandomForest`, `XGBoost`), the `ensemble_metadata.joblib`, and executes forward passes.

## 2. Frozen Model Guarantee
*   **No Retraining:** The simulator contains absolutely no `fit()` calls.
*   **No Weight Mutation:** Ensemble weights are hard-loaded from the Phase 12 JSON/Joblib artifact.
*   **Baseline Reproduction:** The simulator forces a "Baseline Check." The unperturbed input dictionary must produce a prediction that matches the stored `final_holdout_predictions_v3.csv` to within £1. If this constraint fails, the engine throws an integration error.

## 3. Scenario Pipeline
1.  User inputs an altered feature dictionary.
2.  The engine runs an Out-Of-Distribution (OOD) check against training data boundaries.
3.  The dict is converted to a 1-row DataFrame.
4.  The DataFrame passes through `preprocessor.transform()`.
5.  Base models execute `.predict()`.
6.  The weighted average is calculated.
7.  The absolute prediction intervals (Conformal `q_80` and `q_90`) are wrapped around the point estimate.
8.  The Delta (Absolute and Percentage change) from Baseline is returned.

## 4. Out-Of-Distribution (OOD) Detection
Model extrapolation is inherently dangerous. The engine tracks the absolute minimum and maximum observed in the Phase 12 training set for every numeric feature.
If a hypothetical scenario places `Goals/90 = 1.5`, and the historical max is `1.1`, the engine attaches a `WARNING: OOD Feature - goals_per90 exceeds historical maximum (1.1). Interpret cautiously.`

## 5. Non-Causal Interpretation
The output of this simulator reflects **model sensitivity**, not causal market physics.
*   *Incorrect phrasing:* "Increasing age by 2 years decreases value by £5M."
*   *Correct phrasing:* "Under this model scenario, raising age to 28 changes the estimated transfer fee by -£5M."
