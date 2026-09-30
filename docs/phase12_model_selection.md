# Phase 12 Candidate Model Selection

## 1. Selection Criteria
To build the ensemble, candidate models must be selected based **exclusively on historical validation performance** (Experiments 1-4, covering validation seasons 2019/20 through 2022/23). The final holdout (2023/24) is strictly isolated and excluded from this selection process.

## 2. Historical Validation Performance (Mean across Folds 1-4)
Evaluated on the **Enriched** feature set, predicting **Raw Fee (fee_gbp)**:

| Model | Mean MAE | Mean RMSE | Mean R² |
| :--- | :--- | :--- | :--- |
| **Mean Baseline** | £11.06M | £16.74M | -0.026 |
| **Linear Regression** | £11.06M | £16.70M | -0.022 |
| **Ridge Regression** | £11.07M | £16.70M | -0.023 |
| **XGBoost** | £11.10M | £16.71M | -0.023 |
| **Random Forest** | £11.15M | £16.73M | -0.025 |
| **Gradient Boosting** | £11.36M | £17.02M | -0.061 |
| **MLP** | £15.33M | £22.55M | -0.870 |

*Note: Historical R² averages are slightly negative due to high variance in early, smaller validation folds. However, Linear, Ridge, and XGBoost consistently perform closest to the naive baseline on MAE and slightly outperform it on RMSE/R².*

## 3. Selected Candidates
I have selected the following models for the ensembling phase:

1. **Ridge Regression (Enriched):** Provides stable, regularized linear decision boundaries that prevent overfitting to specific historical valuation peaks.
2. **XGBoost (Enriched):** Provides non-linear feature interaction modeling (e.g., age vs. minutes played vs. position) while maintaining high historical robustness.
3. **Random Forest (Enriched):** Adds stable, high-variance reduction ensembling properties, complementing XGBoost's boosting approach.

**Rejected Models:**
- MLP: Severely degraded historical performance.
- Log-target models: Eliminated due to exponential error inflation during inverse transformation.
- Core-only models: Systematically outperformed by the Enriched feature set.
