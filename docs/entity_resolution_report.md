# Entity Resolution Quality Report

## Overview
This document outlines the canonical identity system for the Premier League Transfer Intelligence project. The goal is to accurately unify players, clubs, and seasons across multiple independent datasets without relying on opaque automatic fuzzy matching for uncertain cases. 

*Temporal Rule Enforced:* Entity identity is separate from football performance. Future transfers/information are not used to resolve historical identity.

## Resolution Metrics (Phase 3)

### Player Entities
*   **Total Canonical Players Created:** 667
*   **Total Player Mappings:** 667
*   **Overall Match Rate:** 100% (Base dataset bootstrap phase)
*   **Manual-Review Cases:** 0 
*   **Duplicate / Potential Collisions:** 0 identified in base load.

*Note: The canonical player table was successfully bootstrapped using the FPL dataset (667 unique elements). Because `Understat` did not parse correctly and `Transfermarkt/FBref` were blocked by anti-bot measures, there were no secondary datasets available to map against the master table in this run. Consequently, all 667 records are exact source mappings.*

### Club Entities
*   **Total Canonical Clubs:** 25
*   **Club Identity Mappings:** 40
*   **Notes:** Clubs successfully unified across FPL ("Spurs") and football-data ("Tottenham"). Canonical name standard is the official Premier League name (e.g., "Tottenham Hotspur", "Manchester United").

### Season Entities
*   **Total Canonical Seasons:** 3
*   **Structure:** `season_id` (e.g., `2023_2024`), `season_label` (e.g., `2023/24`).

## Matching Hierarchy (Architecture)
The system strictly executes the following resolution hierarchy to prevent mapping collisions:

1.  **Exact Source IDs:** If a dataset inherently provides cross-platform IDs (rare).
2.  **Existing Cross-Source Mappings:** If a community mapping file is imported.
3.  **Normalized Exact Name + Club + Season:** Exact string match on a normalized name (e.g., lowercase, no accents, no punctuation) *while* playing for the same club in the same season.
4.  **Name + Date of Birth:** Exact normalized name + exact DOB. (Strongest anchor when transferring datasets).
5.  **Name + Club + Season + Position:** Secondary exact match.
6.  **Fuzzy Name Matching (RapidFuzz / difflib):** 
    *   **High Confidence (>90% + matching club):** Automatically mapped.
    *   **Medium Confidence (80-90% + matching club):** Sent to Manual Review Queue.
    *   **Low Confidence (<80%):** Rejected / Unmatched.
7.  **Manual Review Queue:** Saved to `review_queue.csv` for human validation.

## Sanity Checks Performed
*   **Mapping Collisions:** Ensured a single `source_player_id` does not map to multiple `master_player_id`s.
*   **Club Name Relegation/Promotion:** Canonical list accounts for historically varying names (e.g., "Nott'm Forest" vs "Nottingham Forest").
*   **Unresolved Structural Problems:** Currently, our base master player list (derived from FPL) lacks `date_of_birth` and `nationality`. When Transfermarkt data is successfully scraped and parsed, it must take precedence as the base dataset for creating Master Player identities, as DOB is required to safely resolve players who transfer clubs mid-season.
