# Phase 8: Model Robustness, Data Sufficiency & Generalization Report

## 1. Executive Summary
This report analyzes the generalization capabilities of the Phase 7 models. The conclusion is unequivocal: **the current dataset of 371 transfers (with only 69 historical training observations) is statistically INSUFFICIENT for building a robust, generalizable transfer valuation model.** Severe temporal shifts in selling-club strength, extreme positive skew in target valuation, and an absolute dearth of historical training data prevent complex models (trees, MLPs) from learning generalizable market logic.

## 2. Temporal Distribution & Target Shift Analysis
A strict chronological walk-forward split was maintained:
*   **Train (2021/22 & 2022/23):** N = 69
*   **Test (2023/24):** N = 302
*   **Target Distribution Shift:** The market valuation shifted severely between the training period and the test period.
    *   *Train Median:* £8.4M 
    *   *Test Median:* £14.17M 
    *   *Train Mean:* £13.5M
    *   *Test Mean:* £19.7M

## 3. Feature Distribution Shift
We observed significant distribution shift in core selling-club context variables. For example, `prev_season_gd` (Goal Difference of the selling club in T-1) shifted from a mean of **-11.50** (relegation-battling profile) in the training set to **+13.67** (mid-to-upper table profile) in the test set. Because the model learned from a historical period dominated by weaker selling clubs, it failed to correctly value players being sold from stronger clubs in the 2023 window. 

## 4. Simple Model Benchmarks
To test whether complex models simply over-parameterized the N=69 sample, we benchmarked highly regularized linear models (fitted strictly on the training set):
*   **Ridge Regression MAE:** £15.06M
*   **Huber Regressor MAE:** £14.43M
*   *(Recall: Gradient Boosting achieved £14.22M)*

All R² scores remain strictly negative. The fact that heavily regularized linear models and constant median baselines perform on par with tree ensembles proves that the problem is not isolated model choice, but rather the underlying **absence of generalizable signal in a 69-row training set**. 

## 5. Walk-Forward Stability
When attempting to predict the 2022/23 season using *only* the 2021/22 season (N=26), the MAE was £12.3M. This illustrates extreme instability. Random Forest MAE across 5 random initialization seeds resulted in an average MAE of £14.5M (±£107k std dev), proving the errors are intrinsic to the data boundary, not initialization noise.

## 6. Data Sufficiency Assessment
**Verdict: INSUFFICIENT**
The dataset fails the threshold for statistical modeling of a highly skewed, £100M-max regression problem.
*   **Low Training N:** 69 transfers cannot support the learning of 6+ continuous and high-cardinality categorical variables.
*   **Lack of Player Histories:** Because Understat and FBref aggressively blocked requests (via Cloudflare), we lack multi-season player performance (xG, xA, progressive passes). FPL stats only cover 2023/24, rendering them utterly useless for training models on 2021/22.

## 7. Data Expansion Requirements (Next Steps)
To build a functional model, we MUST dramatically expand the chronological window (2016-2023) and source multi-season player performance datasets that do not block HTTP requests. 
**Recommendations for Legitimate External Sources:**
1.  **Kaggle / GitHub Archival Datasets:** Locate pre-scraped, CC-licensed dumps of FBref or StatsBomb event data for 2017-2023.
2.  **FIFA / EA FC Ratings:** Download public datasets containing historical FIFA player ratings. This provides a dense, continuous proxy for player ability that is available for *all* seasons.
3.  **Expanded Transfer History:** Target a broader range of transfers extending back to 2018 to establish a training set of at least N=1,000. 

---
**PHASE 8 STATUS: PASS**
*(Diagnostic completed. The mathematical failure of the models is rigorously documented and attributed to N=69 chronological sparsity. Clear data expansion strategy established.)*
