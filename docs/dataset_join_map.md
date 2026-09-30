# Dataset Join Map & Entity Resolution Strategy

Combining football datasets is notoriously difficult because standard unique identifiers (like a global Player ID) do not exist across independent platforms (e.g., Transfermarkt does not know a player's FBref ID).

This document outlines the architecture for our **Dataset Join Map**, defining how we will securely join Transfermarkt, FBref, Understat, and match data into a unified `player_season_transfers` analytical dataset.

## The Entity Resolution Problem
- **Name Variations:** "Bruno Fernandes" (Transfermarkt) vs "B. Fernandes" (understat) vs "Bruno Miguel Borges Fernandes" (official docs).
- **Special Characters:** "N'Golo Kanté" vs "NGolo Kante".
- **Duplicate Names:** Multiple players named "Adama Traoré" or "Moussa Dembélé".

## 1. Master Player Mapping Table (`player_id_map`)
We will create and maintain a mapping table that bridges all external IDs.

| internal_uuid (Our PK) | player_name_clean | birth_date | tm_id (Transfermarkt) | fbref_id | understat_id | fifa_sofifa_id |
|------------------------|-------------------|------------|-----------------------|----------|--------------|----------------|
| a1b2c3d4...            | bruno fernandes   | 1994-09-08 | 240306                | 507c7bdf | 1228         | 212198         |
| e5f6g7h8...            | ngolo kante       | 1991-03-29 | 225083                | b9fba287 | 338          | 215914         |

### Canonical Entities
To standardize joining, we define a set of canonical key names across the warehouse:
- `player_id` (Our internal UUID)
- `player_name` (Standardized lowercase, unaccented)
- `club_id` (Our internal club UUID)
- `club_name` (Standardized club string)
- `season_id` (Canonical format e.g., "2023_2024")
- `match_id` (Internal match UUID)
- `transfer_id` (Internal transfer UUID)

### Entity Mappings per Source

| Source ID | Canonical Entity Target | Join Key Logic |
|-----------|-------------------------|----------------|
| Transfermarkt | `player_id`, `transfer_id` | `player_name` + `birth_date` + `club_name` + `season_id` |
| FBref | `player_id` | `player_name` + `club_name` + `season_id` |
| FPL API | `player_id` | `player_name` (often split into first/last) + `club_name` |
| FotMob | `player_id`, `match_id` | `player_name` + `club_name` (via squad list) |
| Understat | `player_id` | `player_name` + `club_name` + `season_id` |
| football-data.co.uk | `club_id`, `match_id` | `club_name` + `match_date` + `season_id` |

### Entity Resolution Workflow (How we build the map):
1. **Base Dataset:** Transfermarkt forms the base because it has exact Dates of Birth (DOB) and Transfer Fees (our target).
2. **String Standardization:** All names are lowercased, unaccented (e.g., `Kanté` -> `kante`), and punctuation removed.
3. **Primary Join:** `standardized_player_name` + `birth_year` + `current_club`.
4. **Fuzzy Matching Phase:** If exact match fails, use `thefuzz` (Levenshtein distance) on names combined with `club` and `season` overlap. Matches over 90% confidence are auto-linked; 80-90% require manual review in a notebook.

## 2. Core Entity Join Strategy

### Joining Player Stats to Transfer Fees
- **Target Table:** `transfers_history` (from Transfermarkt)
- **Features Table:** `player_season_stats` (from FBref)
- **Join Logic:** 
  For a transfer occurring in the Summer Window of Season `Y` (e.g., Summer 2022), join the stats from Season `Y-1` (e.g., 2021/2022 season).
  ```sql
  SELECT t.transfer_fee, s.*
  FROM transfers_history t
  JOIN player_id_map m ON t.tm_id = m.tm_id
  JOIN player_season_stats s ON m.fbref_id = s.fbref_id
  WHERE s.season = t.transfer_season - 1
  ```

### Joining Match Context (Club Form / Standings)
- **Target Table:** `transfers_history`
- **Features Table:** `match_results` (from football-data.co.uk)
- **Join Logic:**
  Transfer records contain a `transfer_date` and `selling_club`. We calculate the `selling_club`'s league position, points per game, and Elo rating exactly on `transfer_date - 1 day` by aggregating the `match_results` table.
  *Key Mapping Required:* A `club_name_map` to resolve "Man United" (Transfermarkt) to "Manchester Utd" (FBref) to "Man United" (football-data).

## 3. The Unified Output Dataset
The final unified table for ML training (`unified_transfer_intelligence_df`) will have the following grain: **One Row per Transfer Event**.

*Columns will include:*
- **Identifiers:** `transfer_id`, `internal_uuid`, `player_name`, `season`.
- **Target:** `transfer_fee_eur`, `transfer_fee_inflation_adjusted`.
- **Demographics (TM):** `age_at_transfer`, `nationality`, `position`, `contract_months_remaining`.
- **Historical Stats (FBref):** `prev_season_minutes`, `prev_season_xG_per90`, `prev_season_progressive_passes`.
- **Club Context (football-data):** `selling_club_prestige_index`, `buying_club_prestige_index`.
- **Similar Players (FIFA):** `pace_rating`, `physicality_rating`.
