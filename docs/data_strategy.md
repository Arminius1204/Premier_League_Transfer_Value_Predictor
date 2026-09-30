# Data Strategy

## Core Principle
The final training dataset MUST be constructed by joining multiple independent football datasets rather than relying on one pre-made dataset. We will not download random datasets just to increase the dataset count. Each dataset must have a documented, specific purpose for the valuation engine.

## Dataset Registry Design

For every dataset integrated into the project, we will maintain an entry in the Dataset Registry with the following schema:

- **Dataset Name:**
- **Source:** (e.g., Transfermarkt, FBref, StatsBomb, Understat, FIFA)
- **URL/API:** (Link to the data source or API endpoint)
- **Coverage:** (Leagues, competitions)
- **Seasons:** (e.g., 2010/11 to 2023/24)
- **Granularity:** (e.g., Season-level, Match-level, Event-level)
- **Important Columns:** (Key features like `transfer_fee_eur`, `xG_per_90`, `minutes_played`)
- **License/Usage Constraints:** (e.g., Non-commercial use, attribution required)
- **Join Strategy:** (How it joins to other datasets - e.g., fuzzy matching on player name + birth date, or mapping via a unified Player ID table)
- **Purpose:** (Training, Enrichment, Validation, or Analysis)

## Data Integration Pipeline

1. **Collection (`ml/data_collection`):** Python scripts (using `requests`, `BeautifulSoup`, or API clients) to gather data.
2. **Cleaning (`ml/data_cleaning`):** Handling missing values, standardizing player names, currency conversions (adjusting for inflation).
3. **Validation (`ml/data_validation`):** Ensuring data types are correct, checking for duplicate records, validating statistical ranges.
4. **Engineering (`ml/feature_engineering`):** Creating per-90 stats, position-aware features, rolling averages, and contextual features (e.g., club prestige, contract remaining).
