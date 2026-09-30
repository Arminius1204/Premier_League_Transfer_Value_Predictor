# Phase 6: Leakage-Safe Feature Engineering Report

## 1. Feature Engineering Methodology & Temporal Validity
The fundamental modeling observation is **ONE ROW = ONE ELIGIBLE TRANSFER EVENT**.
We successfully transformed the canonical warehouse into a strictly leakage-safe candidate feature matrix. 
*   Every predictor represents information that was mathematically available *before* the proxy transfer date (`T-1`). 
*   FPL historical statistics are only mapped if the transfer explicitly occurred *after* the statistics were finalized.
*   Selling club standings are strictly pulled from the prior completed season (`T-1`).

## 2. Feature Sets & Missing Data Strategy
Due to the legal block on Understat/FBref, historical player-level on-ball performance features are largely absent for 2021/22 and 2022/23. 
Therefore, we explicitly split the feature space:

### `FEATURE_SET_CORE`
*   Features: `age_at_transfer`, `position`, `nationality`, `selling_club_id`
*   Coverage: ~100% across all 371 transfers.
*   Imputation Strategy: Unmapped clubs and positions were gracefully preserved as `"UNKNOWN"`. Missing ages are preserved as NULL (not zero-imputed).

### `FEATURE_SET_ENRICHED`
*   Features: `prev_season_points`, `prev_season_points_per_match`, `prev_season_gd`, `prev_season_goals_per90`, `prev_season_xg_per90`, `low_minutes_flag`
*   Coverage: Variable. Player-level stats strictly cover 2023/24 transfers (via 2022/23 FPL data). Club-level context maps successfully to most Premier League selling clubs across all seasons.
*   Imputation Strategy: `per90` metrics strictly filter out dividing-by-zero (if `minutes == 0`, output is NULL).

## 3. Position Normalization
Transfermarkt positions were robustly consolidated into four primary macro-roles:
*   `GOALKEEPER`
*   `DEFENDER` (Includes Centre-Back, Left-Back, Right-Back)
*   `MIDFIELDER` (Includes Defensive, Central, Attacking, Left/Right Midfield)
*   `FORWARD` (Includes Centre-Forward, Winger, Second Striker)

Original raw position values were explicitly retained in `position_raw`.

## 4. Leakage Audit
*   **Target Aliases:** Audited and cleared. `fee_gbp` is the strictly isolated target. `raw_fee_string`, `fee_numeric`, and `fee_currency` were intentionally dropped from the candidate dataset.
*   **Post-Transfer Knowledge:** CLEARED. We successfully avoided implementing Current Market Value or Current Wage data which would have severely contaminated the model.
*   **Destination Club:** We explicitly omitted `destination_club` features to strictly evaluate the player's intrinsic market value prior to the buyer's financial status inflating the fee.

## 5. Target Distribution & Transformation (EDA)
A visual EDA was conducted on the 371 eligible transfers using custom scalable SVG charts (saved to `/docs/figures/`).
*   **Min Fee:** £85,900
*   **Max Fee:** £100,159,400 (Declan Rice benchmark)
*   **Median Fee:** £12,885,000
*   **Mean Fee:** £18,615,303
*   **Skewness:** 1.85
*   **Conclusion:** The raw distribution is highly right-skewed. Therefore, we computed `log_fee_gbp` (`log1p` transformation), which effectively normalizes the tail. The model architecture should evaluate both targets, but `log_fee_gbp` is highly recommended.

## 6. Sample Size Finalization
Out of 1,300 total transfers tracked:
*   **Eligible Disclosed Target Sample:** 371 transfers.
*   **2021/22:** 26
*   **2022/23:** 43
*   **2023/24:** 302
*   **Duplicates:** 0 (Verified via transfer_id constraints).

## 7. Pytest Validation
The automated `pytest` suite was successfully expanded to cover feature-engineering constraints:
*   `test_no_target_leakage`: Passed
*   `test_demographics_validity`: Passed (All ages are safely bounded between 15 and 45)
*   `test_per90_validity`: Passed (Zero minutes safely throw NULL per-90s, completely eliminating `ZeroDivisionError` risks)
*   `test_positive_fee`: Passed
*   `test_unique_transfers`: Passed

## 8. Limitations & Recommendations for Phase 7
**Limitation:** The lack of granular historical FPL/Understat data means that models trained on `FEATURE_SET_ENRICHED` will suffer severe row-dropping for older seasons.
**Recommendation:** We strongly recommend evaluating a baseline model strictly on `FEATURE_SET_CORE` + `Club Context`, which enjoys ~100% historical density and relies on the strong demographic drivers of football transfer valuations.

---
**PHASE 6 STATUS: PASS**
*(Candidate matrix is generated, documented, completely leakage-free, and validated by unit tests. Ready for ML modeling).*
