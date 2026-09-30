# Phase 10: Expanded Warehouse Audit

## 1. Overview
This audit inspects the `data/processed/` directory following the Phase 9 expansion.

## 2. Table Summaries
*   **players.csv:** 4,799 rows
*   **clubs.csv:** 28 rows (Unique Premier League clubs participating from 18/19 to 23/24)
*   **seasons.csv:** 6 rows (2018/19 through 2023/24)
*   **matches.csv:** 2,280 rows (Exactly 380 matches × 6 seasons)
*   **club_season_context.csv:** 120 rows (Exactly 20 clubs × 6 seasons)
*   **player_seasons.csv:** 4,383 rows (FPL player performance statistics across 6 seasons)
*   **transfers_normalized.csv:** 2,830 rows
*   **transfer_performance_links.csv:** 781 rows (Eligible Disclosed Permanent Transfers properly linked to temporal windows)

## 3. Breakdown by Season

| Season | Matches | Club Contexts | FPL Player Records | Total Transfers | Target Eligible Transfers |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **2018/19** | 380 | 20 | 624 | 476 | 136 |
| **2019/20** | 380 | 20 | 666 | 476 | 124 |
| **2020/21** | 380 | 20 | 713 | 434 | 100 |
| **2021/22** | 380 | 20 | 737 | 443 | 112 |
| **2022/23** | 380 | 20 | 778 | 502 | 158 |
| **2023/24** | 380 | 20 | 865 | 499 | 151 |
| **Total** | **2,280** | **120** | **4,383** | **2,830** | **781** |

## 4. Missingness & Duplicate Audit
*   **Duplicates:** Zero duplicate `match_id`, zero duplicate `(master_player_id, season_id)` combinations in FPL, zero duplicate `transfer_id`.
*   **Missingness:** Target variable `fee_gbp` missingness is 0% for `target_eligible == True`. Player DOB missingness is present for some historically obscure players and must be handled carefully during age calculation.

## 5. Source Coverage
*   **Transfermarkt:** Full coverage (2018-2024)
*   **football-data.co.uk:** Full coverage (2018-2024)
*   **FPL Historical (vaastav):** Full coverage (2018-2024)
*   **Understat / FBref:** 0% (Blocked)
*   **Capology:** 0% (Blocked)
