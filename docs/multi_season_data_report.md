# Multi-Season Data & Transfer Parsing Report

## 1. Multi-Season Acquisition Strategy
We have expanded the dataset ingestion horizon to capture three active Premier League seasons: `2021/22`, `2022/23`, and `2023/24`.

*   **FPL API:** Only native current-season (`2023/24`) endpoint is available. Historical records require either unauthorized external repos or web archive parsing. In accordance with the non-fabrication/legal-acquisition constraints, FPL is locked to `2023/24` in our direct pipeline.
*   **football-data.co.uk:** Successfully acquired historical match records for all three target seasons.
*   **Understat:** Successfully acquired HTML for all three seasons.
*   **Transfermarkt:** Successfully acquired HTML for all three seasons.

## 2. Transfermarkt Parser Validation
The parser has been completely overhauled using `beautifulsoup4` to structurally index the exact Transfermarkt HTML outputs.

*   **Transfer Target Scheme Defined:** The system explicitly classifies `fee_status` into `DISCLOSED`, `UNDISCLOSED`, `FREE`, and `LOAN`. 
*   **Zero-Masking Prevented:** `UNDISCLOSED` fees are strictly preserved as categorical identifiers (not imputed as £0) to prevent severe target leakage.
*   **Timing Independence:** `season_id` guarantees that a transfer occurring in August 2023 will only be joined against `2022/23` (previous season) performance stats in the downstream ML matrix.

## 3. Understat Parser Validation (Structural Limitation)
*   **Limitation Identified:** The `playersData` JSON structure does *not* exist on the Understat league-level page (`/league/EPL/2023`). The league page strictly hosts `teamsData` and `datesData`. 
*   **Fix Implemented:** The parser was migrated to correctly extract the embedded `teamsData` instead, ensuring we have robust xG/xGA metrics at the club level. To acquire player-level xG, future scrapers must target individual team URLs.

## 4. Entity Resolution & Cross-Source Matching (Stress Test)
With Transfermarkt parsed, we successfully stress-tested the `PlayerResolver` by projecting Transfermarkt entities against the FPL Master Base.

*   **Master Players Created:** 1042
*   **Total Identity Mappings:** 1163
*   **Exact Normalised Matches:** Successfully matched hundreds of TM players to their FPL counterparts.
*   **Fuzzy Name Matching:** Captured minor variations.
*   **Review Queue Generated:** 7 players flagged for human review due to unicode discrepancies across sources (e.g., `HÃ¡kon Valdimarsson` vs `Hakon Valdimarsson`, `Mateo Kovacic` vs `Mateo Kovačić`).
*   **Club History:** Supported natively (Transfermarkt outputs contain zero implicit assumption of a permanent club).
*   **DOB:** Because FPL lacks DOB, DOB remains empty in the master record. As previously noted, when a full Transfermarkt scrape runs, TM should assume the role of the Base Master Table so that `date_of_birth` populates the canonical anchor.

## 5. Dataset Size Report

| Source | Season | Raw Files | Parsed Rows | Unique Players | Unique Clubs | Errors |
|--------|--------|-----------|-------------|----------------|--------------|--------|
| FPL | 2023/24 | 1 | 667 | 667 | 20 | 0 |
| football-data | 2021/22 | 1 | 380 | 0 | 20 | 0 |
| football-data | 2022/23 | 1 | 380 | 0 | 20 | 0 |
| football-data | 2023/24 | 1 | 380 | 0 | 20 | 0 |
| Transfermarkt | 2021/22 | 1 | 443 | 425 | 0 | 0 |
| Transfermarkt | 2022/23 | 1 | 502 | 489 | 0 | 0 |
| Transfermarkt | 2023/24 | 1 | 499 | 488 | 0 | 0 |
| Understat | All | 3 | 0 (Player)* | 0 | 20* | 0 |

*\* Note: Understat teamsData successfully extracts 20 clubs per season. The player row count is accurately reported as 0 due to the structural limitation documented above.*
