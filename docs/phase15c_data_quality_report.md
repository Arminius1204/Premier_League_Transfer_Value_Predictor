# Phase 15C: Data Quality and Missingness Audit

## 1. Executive Summary
This report analyzes the missingness of features in the Premier League Transfer Intelligence dataset (`transfer_features_enriched_v2.csv`). The purpose is to identify which features have sufficient coverage to be included in a leakage-free transfer-fee model (V4), and which features require architectural improvements (Phase 16).

## 2. General Missingness Audit

The following table details the missingness percentage for every feature with missing values, out of a total of 781 valid transfer records.

| Feature Name | Missingness (%) | Root Cause |
| :--- | :--- | :--- |
| `age_at_transfer` | 100.0% | FPL data lacks `date_of_birth`. Transfermarkt age is not systematically parsed. |
| `age_squared` | 100.0% | Derivative of missing age. |
| `selling_club_pts_t1` | 100.0% | `from_club_id` in transfer records fails to join against historical matches. |
| `selling_club_gd_t1` | 100.0% | Derivative of missing club mapping. |
| `two_season_avg_minutes` | 84.9% | Requires player to have T-1 AND T-2 season data in the Premier League (FPL). |
| `two_season_avg_goals` | 84.9% | Requires player to have T-1 AND T-2 season data. |
| `goals_trend` | 84.9% | Requires player to have T-1 AND T-2 season data. |
| `t1_assists_per90` | 77.3% | Requires T-1 data AND minutes > 0. |
| `t1_bps_per90` | 77.3% | Requires T-1 data AND minutes > 0. |
| `t1_goals_per90` | 77.3% | Requires T-1 data AND minutes > 0. |
| `t1_minutes` | 74.9% | Missing for transfers entering the Premier League from foreign leagues, or missing FPL history. |
| `t1_goals` | 74.9% | See above. |
| `t1_assists` | 74.9% | See above. |
| `t1_bps` | 74.9% | See above. |

## 3. Player-Season Coverage Tiers

The entity resolution pipeline relies exclusively on Fantasy Premier League (FPL) data to bootstrap the identity graph. Consequently, the coverage tiers are heavily biased towards domestic transfers:

*   **Tier 1: Continuous Domestic (15% Coverage):** Players with continuous FPL history (T-1 and T-2). These players have full feature coverage for performance trends. Example: Jack Grealish (Aston Villa -> Man City).
*   **Tier 2: Immediate Domestic (10% Coverage):** Players with T-1 FPL history but lacking T-2. These players have standard T-1 features.
*   **Tier 3: Foreign Imports (75% Coverage):** Players transferring into the Premier League from foreign leagues, or players whose FPL data could not be mapped. These players have **0% performance feature coverage** natively. Example: Erling Haaland (Dortmund -> Man City), until manually patched via supplementary data.

## 4. Entity Resolution Fix

The high missingness in Tier 3 was exacerbated by a bug in `player_resolver.py`, where FPL players were assigned a new, unique `master_player_id` for every season file they appeared in. This prevented multi-season FPL data from aggregating under a single canonical ID, causing performance joins to fail.
- **Action Taken:** Deduplication logic was moved to track global identity across all seasons. `Master Players Created` dropped from 4,795 to 2,338.
- **Haaland Test:** The manual supplementary data for Erling Haaland was properly merged with his Transfermarkt identity. Haaland now possesses valid T-1 performance data (`minutes: 1914`, `goals: 22`).

## 5. Candidate Feature Strategy (V4 Model)

Given the high missingness in performance and demographic features, the V4 Leakage-Free Transfer-Fee Model will be strictly constrained to avoid dropping 75% of the dataset:

*   **Target:** `log_fee_gbp` (derived from actual transfer fee)
*   **Leakage Removal:** `market_value` will NOT be used, as it leaks future post-transfer valuations.
*   **Imputation Strategy:** 
    *   T-1 performance metrics will be mean/median-imputed with a binary missingness indicator (`is_foreign_import`).
    *   Age and Club Context features will be excluded entirely from V4 until data parsing is improved in Phase 16.

**Approved V4 Features:**
`position`, `previous_transfer_count`, `career_minutes_before_transfer`, `career_goals_before_transfer`, `is_summer_window`, `t1_minutes` (imputed), `t1_goals` (imputed), `t1_assists` (imputed).
