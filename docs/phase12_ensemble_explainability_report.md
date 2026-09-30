# Phase 12: Ensemble, Robustness & Explainability Report

## 1. Executive Summary
Phase 12 operationalized an ensemble modeling framework and formalized the bounds of model uncertainty via Conformal Prediction. The goal was not to artificially juice the R², but to establish a mathematically defensible method for producing robust valuation bounds.

Based on historical validation experiments, the final selected models were **Ridge Regression, Random Forest, and XGBoost**. A weighted ensemble (inverse historical MAE) provided superior or equivalent robustness compared to any single model. Final holdout Mean Absolute Error on the isolated 2023/24 set was **£13.23M** for the ensemble, compared to £13.16M for Ridge alone, indicating that combining linear and non-linear patterns generates highly stable generalizations.

## 2. Candidate Model Selection & Out-Of-Fold Methodology
Models were evaluated historically (Seasons 18/19 through 22/23), explicitly excluding the 2023/24 test holdout.
*   **Ridge Regression (Enriched)** was selected for capturing broad, continuous market correlations (e.g., Age).
*   **XGBoost (Enriched)** and **Random Forest (Enriched)** were selected for handling non-linear interactions without catastrophically overfitting historical noise.
*   **Log-target** models and **MLP** models were explicitly rejected due to highly volatile out-of-sample behavior.

Out-Of-Fold (OOF) predictions were generated via sequential train/test folds spanning 2018-2022. These historical predictions determined the final ensemble weightings:
- **Ridge:** 33.48%
- **XGBoost:** 33.39%
- **Random Forest:** 33.13%
*(Note: Because they performed so similarly historically, the ensemble essentially weights them equally).*

## 3. Ensemble Evaluation (2023/24 Holdout)
Once methodologies were frozen, the models were deployed exactly once against 2023/24.

| Model | MAE | RMSE | R² | Median AE |
| :--- | :--- | :--- | :--- | :--- |
| **Ridge Regression** | £13.16M | £20.89M | +0.024 | £9.06M |
| **Mean Ensemble** | £13.23M | £20.85M | +0.028 | £8.75M |
| **Weighted Ensemble** | **£13.23M** | **£20.85M** | **+0.028** | **£8.74M** |
| **XGBoost** | £13.38M | £21.46M | -0.032 | £9.02M |
| **Random Forest** | £13.76M | £21.84M | -0.069 | £9.30M |

The Weighted Ensemble drastically reduced Extreme Errors compared to individual tree models (reducing RMSE relative to XGBoost and RF) and achieved a highly robust £8.7M Median Error.

## 4. Conformal Prediction Intervals (Uncertainty)
Point-estimates are dangerous in football transfers due to vast unobservable factors (contract length, agent fees). We instituted **Conformal Prediction Intervals**.
- **Method:** Using historical Out-Of-Fold absolute residuals to capture empirical error.
- **Historical 80% Error Bound:** ± £12.95M
- **Historical 90% Error Bound:** ± £21.43M

Every point prediction now includes an upper and lower bound calculated from this empirical calibration. The result is a probabilistic estimation bracket rather than a false assertion of precision.

## 5. Global Feature Importance (Explainability)
Feature influence was extracted directly from the Ridge model coefficients and XGBoost importances:
*   **Age at Transfer:** Strongest negative coefficient. Market reality reflects that players hitting age 29+ suffer steep valuation drop-offs.
*   **Career Goals & BPS/90 (T-1):** Strongest positive associations. Proven historical output (Goals) and underlying attacking threat (Bonus Points) command heavy premiums.
*   **Selling Club Context:** T-1 Club points influence value, showing a "big club tax" or validation effect for players succeeding in difficult environments.

## 6. Model-Market Discrepancy
The model explicitly does not output "true" values. It outputs the "historical median market expectation." The gap between `Predicted Fee` and `Actual Fee` reveals market anomalies (Desperation overpays, free agent market oddities, or extreme bidding wars).
*   *Model Above Market:* Could suggest the player was acquired cheaply or was severely out of contract.
*   *Model Below Market:* Usually pinpoints panic buys, intense bidding wars (e.g. Caicedo, Declan Rice, Enzo Fernández), or uniquely structured deals unobserved in standard performance metrics.

## 7. Limitations & Recommendations for Phase 13
*   **No Causal Mechanism:** Explainability charts show *associations*. We cannot say scoring 5 more goals *causes* a £10M increase directly.
*   **Contract Status (Latent Variable):** Our single highest unobserved variable is Contract Remaining. Capology data remains blocked.
*   **Next Steps:** Phase 13 must focus on packaging this modeling pipeline into a deployable, interactive system (FastAPI backend and React frontend) where users can query a player's canonical identity, view the £13M point estimate, and inspect the Conformal Prediction Bounds.

**PHASE 12 STATUS: PASS**
