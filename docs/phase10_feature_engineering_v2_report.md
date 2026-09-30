# Phase 10: Historical Feature Engineering 2.0 Report

## 1. Executive Summary
Following the successful Phase 9 data expansion, Phase 10 rebuilt the feature engineering matrix entirely from scratch to handle the new 6-season timeframe (2018/19 - 2023/24). The focus remained strictly on creating a **leakage-safe** tabular dataset where every single predictor explicitly represents information available *before* the transfer date.

**Final Datasets Generated:**
*   `transfer_features_core_v2.csv`: Broad historical coverage (Demographics, Club Context, Career Totals).
*   `transfer_features_enriched_v2.csv`: Includes deep historical FPL metrics (goals, assists, bps, per90s, form trends).

**Total Eligible Observations:** 781 (Exactly 1 Row = 1 Disclosed Permanent Transfer).

## 2. Expanded Warehouse Audit
The underlying warehouse consists of:
*   2,830 Total normalized transfers.
*   4,383 FPL player-season records covering 6 consecutive Premier League seasons.
*   2,280 match records providing robust selling-club context metrics (Points, GF, GA, GD).
*   Coverage is 100% complete for Transfermarkt, FPL historical (Vaastav archive), and football-data.co.uk. FBref and Understat remain blocked and excluded.

## 3. FPL Temporal-Validity Analysis
A comprehensive temporal audit (`docs/fpl_temporal_validity.md`) proved that FPL season-end records present a severe target-leakage danger if mapped to mid-season transfers (e.g., matching a January 2022 transfer to 2021/22 season-end FPL stats). 

**Decision:** All FPL records were strictly lagged. Only statistics from a *fully completed* season occurring chronologically *before* the transfer date were linked to a player transfer. 

## 4. Feature Groups Engineered
The new dataset categorizes features rigorously:
*   **Demographics:** Age at transfer, `age_squared`, normalized `position` (Goalkeeper, Defender, Midfielder, Forward).
*   **Player Performance (T-1):** `t1_minutes`, `t1_goals`, `t1_assists`, `t1_bps`, `t1_low_minutes_flag`.
*   **Per-90 Metrics (T-1):** Goals/90, Assists/90, BPS/90 (Proxy for xG/Attacking Threat).
*   **Two-Season Form:** Average goals and minutes across T-1 and T-2, plus directional `goals_trend`.
*   **Career Experience:** `career_minutes_before_transfer`, `career_goals_before_transfer` (sum of all seasons < T).
*   **Transfer History:** `previous_transfer_count`, `previous_transfer_fee_gbp` (using the highest date < current transfer date).
*   **Selling Club Context (T-1):** `selling_club_pts_t1`, `selling_club_gd_t1`.
*   **Transfer Context:** `transfer_month`, `is_summer_window`.

## 5. Missing-Data Strategy
*   Missing FPL history (e.g., player was in a foreign league the previous year) is preserved as `NaN` rather than a zero value, differentiating "didn't play in the PL" from "played in the PL and scored 0 goals."
*   Low-minute PL players (< 450 minutes) have a binary `t1_low_minutes_flag` to allow tree-based algorithms to down-weight noisy Per-90 variations.

## 6. Target & Feature Distribution Audit
*   The target variable `fee_gbp` ranges from roughly £500k to £100M+ across the 781 samples.
*   A `log_fee_gbp` column was generated via `np.log1p(fee_gbp)` to correct right-skewness.
*   10 comprehensive plots were generated and saved in `docs/figures/feature_engineering_v2/` mapping fee distributions, age vs fee, and BPS/90 vs fee.

## 7. Leakage & Correlation Audit
*   All destination-club metrics (e.g., `to_club_id`) have been entirely scrubbed from the feature set.
*   All target aliases (`raw_fee_string`, `fee_numeric`) are removed.
*   Tested strictly via `pytest`: All 30 tests in the testing suite passed, verifying 1-to-1 row mappings, strictly positive minutes, and valid age bounds.
*   Correlation heatmaps generated via `plot_features_v2.py` confirm strong intuitive links (e.g., BPS/90 strongly correlates with offensive player valuations).

## 8. Sample-Size Analysis
*   **2018/19:** 136 Eligible
*   **2019/20:** 124 Eligible
*   **2020/21:** 100 Eligible
*   **2021/22:** 112 Eligible
*   **2022/23:** 158 Eligible
*   **2023/24:** 151 Eligible
*   **Total N:** 781

## 9. Recommendations for Phase 11
The dataset has matured from a fragile N=69 training set to a robust N=781 temporal frame. Phase 11 can now safely instantiate rolling time-series cross-validation models without the previous fear of data insufficiency. 

**PHASE 10 STATUS: PASS**
