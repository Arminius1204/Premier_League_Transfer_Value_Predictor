# Data Parsing & Profiling Report

## 1. Dataset Temporal Validity Classification
To prevent data leakage during ML modeling, all potential features are classified based on their temporal validity relative to a transfer event.

*   **A. Safe before transfer:** Age at transfer date, contract months remaining, historical match results from previous seasons, historical goals/assists.
*   **B. Potentially leakage-prone:** "End of season" standings for the season in which a mid-season (January) transfer occurs, rolling averages that don't enforce a strict `date < transfer_date` condition.
*   **C. Post-transfer:** New club performance, goals scored *after* the transfer, future FIFA ratings.
*   **D. Unknown timing:** Transfermarkt "market values". (Market values are updated arbitrarily and may lag behind real-world events. Using current market value to predict transfer fee is highly leakage-prone as the value is often updated *because* of the transfer).

## 2. Dataset Role Classification
Each dataset serves a specific, documented purpose within the ML architecture.

*   **FPL:** Core / Enrichment (Provides primary player stats: goals, assists, minutes, xG, xA).
*   **Understat:** Core advanced analytics (Shot-level expected goals mapping).
*   **football-data.co.uk:** Core match/team context (Used to compute Elo ratings, club form, and league position at transfer time).
*   **Transfermarkt:** Core Target Data (Source of the dependent variable `transfer_fee_eur` and critical demographics).
*   **Capology:** Enrichment (Wage structures heavily influence transfer negotiations).
*   **FotMob:** Validation / Backup (Alternative source for match ratings).

## 3. Parsing Profiles
*Profiling results are generated from the `data/parsed/` output files without performing final entity resolution.*

### FPL (`fpl_parsed_2023_2024.csv`)
*   **Source Identifiers Preserved:** `source_player_id`, `source_player_name`, `source_club_id`, `source_club_name`
*   **Row Count:** 667
*   **Column Count:** 12
*   **Unique Players:** 667
*   **Unique Clubs:** 20
*   **Missingness:** 0% on core stats (minutes, goals).
*   **Example Columns:** `goals_scored`, `assists`, `expected_goals`, `now_cost`

### football-data.co.uk (`football_data_parsed_2023_2024.csv`)
*   **Source Identifiers Preserved:** `source_match_id`, `source_home_team`, `source_away_team`
*   **Row Count:** 380
*   **Column Count:** 7
*   **Unique Clubs:** 20
*   **Missingness:** 0% on goals and dates.
*   **Example Columns:** `home_goals`, `away_goals`, `match_date`

*Note: Understat HTML payload was acquired, but the specific JSON payload regex did not extract successfully in this initial parsing run. FBref and Capology returned 403 blocks during acquisition.*
