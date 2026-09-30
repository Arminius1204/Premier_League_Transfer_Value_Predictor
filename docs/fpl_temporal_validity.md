# FPL Temporal Validity Audit

## 1. Description of the Source
The Fantasy Premier League (FPL) Historical dataset (via the Vaastav archive) contains end-of-season snapshots for every Premier League player from 2018/19 through 2023/24. 

## 2. Temporal Representation
**What period do the statistics represent?**
Each FPL CSV file represents the cumulative statistics of a player at the *end* of that specific Premier League season (Game Week 38).

**Are there mid-season historical snapshots?**
While the Vaastav repository does track week-by-week data, our current parser aggregates/utilizes the `cleaned_players.csv` (season-end summary).

## 3. Transfer Window Implications
Because we are using season-end totals:

*   **Summer Transfer Window (July-August):** 
    *   Occurs *after* Season T-1 has completed, but *before* Season T begins.
    *   **Validity:** The season-end statistics for Season T-1 are **VALID**.
    *   **Example:** A transfer in July 2022 can validly use 2021/22 FPL statistics.

*   **Winter Transfer Window (January):**
    *   Occurs *during* Season T.
    *   **Validity:** The season-end statistics for Season T-1 are **VALID**. 
    *   **Target Leakage Danger:** Using Season T statistics for a January Season T transfer is **INVALID**. The Season T file includes goals scored in February, March, April, and May, which occur *after* the transfer date.

## 4. Feature Classification

| Potential FPL Feature | Classification | Reason |
| :--- | :--- | :--- |
| `previous_season_goals` | **VALID** | Season T-1 is complete before any Season T transfer. |
| `previous_season_minutes` | **VALID** | Complete before Season T transfer. |
| `previous_season_bps` | **VALID** | Complete before Season T transfer. |
| `current_season_goals` | **INVALID** | For summer transfers, the season hasn't started. For winter transfers, the season-end total includes future events (post-transfer). |
| `fpl_now_cost` | **INVALID** | Player valuations fluctuate during the season and represent fantasy game constraints, not real-world market values. |

## 5. Conclusion
**All FPL statistics must be lagged by at least one season (T-1).** 
No current-season (T) FPL statistics will be allowed into the feature matrix, ensuring 100% protection against temporal target leakage.
