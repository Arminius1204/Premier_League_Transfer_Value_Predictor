# Phase 9: Historical Dataset Expansion & Performance Integration Report

## 1. Executive Summary
Phase 9 successfully solved the "Insufficient Data" crisis identified in Phase 8 without resorting to scraping blocked domains (FBref/Understat). By leveraging the canonical Vaastav Fantasy Premier League historical archive and fetching historical Transfermarkt and football-data.co.uk snapshots, the chronological dataset was doubled from 3 seasons to 6 seasons (2018/19–2023/24). 

The raw dataset expansion yielded a massive increase in statistically viable training rows, growing the eligible disclosed transfers from **371** to **781** while introducing dense, multi-season player performance metrics.

## 2. Sources Investigated & Decisions
1. **Vaastav FPL Historical Archive:** (ACCEPTED as CORE)
   *   *Coverage:* 2018/19 – 2023/24. 
   *   *Fields:* Minutes, goals, assists, bps, threat, influence.
   *   *Quality:* Exceptionally high. Sourced originally from the official FPL API, carefully warehoused on GitHub. Contains robust player names for Entity Resolution.
2. **Transfermarkt Historical:** (ACCEPTED as CORE)
   *   *Coverage:* 2018/19 – 2023/24.
   *   *Quality:* Complete preservation of text strings, native currencies, and dates.
3. **football-data.co.uk:** (ACCEPTED as CORE)
   *   *Coverage:* 2018/19 – 2023/24 match results.
4. **EA FC / FIFA Kaggle Datasets:** (REJECTED / DEFERRED)
   *   *Reasoning:* With FPL data spanning the exact same 6 seasons, actual on-pitch statistics are now available. Introducing video game proxies risks muddying actual performance metrics and violating the project's statistical integrity constraint.
5. **Understat / FBref:** (REJECTED)
   *   *Reasoning:* Explicitly blocked by Cloudflare. Strictly avoided to comply with ethical web practices and user constraints.

## 3. Entity Resolution Expansion
The massive influx of historical FPL data required a comprehensive rerun of the entity resolution pipeline:
*   **Master Seasons Created:** 6
*   **Master Clubs Configured:** 28
*   **Master Players Created:** 4,799
*   **Player Identity Mappings:** 7,627 
*   **Review Queue:** 78 (Fuzzy score < 90). The vast majority of players auto-matched (Score >= 90) or created distinct identities.

## 4. Feature and Temporal Validity
A new artifact `feature_temporal_validity.csv` has been generated, explicitly encoding information leakage rules:
*   `previous_season_goals` (T-1) is tagged **VALID** for summer transfers.
*   `current_season_goals` (T) is tagged **INVALID** to prevent target leakage.
*   The `transfer_performance_links.csv` correctly bridges a Transfer ID happening in Season T to the `player_seasons.csv` corresponding to Season T-1.

## 5. Sample Size Expansion Results
The warehouse build step recalculated all metrics on the newly mapped ecosystem.

| Season | Total Transfers | Disclosed Eligible |
| :--- | :--- | :--- |
| **2018/19** | 476 | 136 |
| **2019/20** | 476 | 124 |
| **2020/21** | 434 | 100 |
| **2021/22** | 443 | 112 |
| **2022/23** | 502 | 158 |
| **2023/24** | 499 | 151 |
| **Total** | **2,830** | **781** |

*(Note: Player performance linkage will drop some non-PL players from lower leagues depending on prior-year FPL availability, but the upper bound of 781 is a spectacular improvement over 371.)*

## 6. Data Quality Results
All 22 Pytest validation checks passed on the expanded warehouse.
*   Zero duplicate transfer IDs.
*   Zero duplicate player-season pairs.
*   Zero target leakage between T and T-1 matching.
*   FX conversion handles 2018-2023 EUR-to-GBP correctly based on historic July rates.

## 7. Recommendations for Phase 10
The data foundation is now wide enough and deep enough to support statistical learning. We should proceed to Phase 10 (Feature Engineering) by executing the temporal joins on the newly linked `transfer_performance_links.csv`, uniting Transfermarkt fee labels, football-data club contexts, and FPL player statistics into the final ML matrix.

---
**PHASE 9 STATUS: PASS**
