# Dataset Registry

This registry tracks the publicly accessible and legally usable sources that form the ecosystem of the Premier League Transfer Intelligence & Player Valuation Engine.

## Core Data Sources

### 1. Transfermarkt (Market & Transfer Data)
- **URL:** https://www.transfermarkt.com
- **API Availability:** Direct HTML scraping.
- **Python `requests` Compatibility:** High, but requires custom User-Agent headers and strict rate-limiting (5s sleep) to avoid IP bans.
- **Seasons Covered:** 2018/19 - 2023/24 (Parsed & Verified).
- **Data Granularity:** Player-level, Transfer-level (event).
- **Important Fields:** `transfer_fee_eur`, `date_of_birth`, `nationality`, `joined_club`.
- **Quality Status:** High. Fully integrated into the warehouse.

### 2. football-data.co.uk (Match Context & Club Form)
- **URL:** https://www.football-data.co.uk/englandm.php
- **API Availability:** Direct CSV downloads per league/season.
- **Python `requests` Compatibility:** 100% compatible. Fast static file downloads.
- **Seasons Covered:** 2018/19 - 2023/24 (Parsed & Verified).
- **Data Granularity:** Match-level.
- **Important Fields:** `HomeTeam`, `AwayTeam`, `FTHG`, `FTAG`.
- **Quality Status:** High. Clean structural format. Fully integrated into the warehouse.

### 3. Vaastav Fantasy Premier League Historical Archive (Performance Data)
- **URL:** https://github.com/vaastav/Fantasy-Premier-League
- **API Availability:** Raw CSV downloads from GitHub.
- **Python `requests` Compatibility:** 100% compatible.
- **Seasons Covered:** 2018/19 - 2023/24 (Parsed & Verified).
- **Data Granularity:** Player-season.
- **Important Fields:** `minutes`, `goals_scored`, `assists`, `bps` (Bonus Points System), `creativity`, `threat`, `influence`.
- **Quality Status:** High. Serves as the primary player-performance dataset after the blocking of FBref/Understat. Fully integrated into the warehouse.

## Blocked / Rejected Sources

### 4. FBref via Opta (Performance Data)
- **Status:** **BLOCKED**. Returns HTTP 403 due to Cloudflare anti-bot measures. 
- **Decision:** Excluded from the active pipeline to comply with ethical web practices.

### 5. Understat (Expected Goals & Shot Data)
- **Status:** **BLOCKED**. TeamsData JSON payload is consistently obfuscated or blocked by Cloudflare in the current environment.
- **Decision:** Excluded from the active pipeline.

### 6. Capology (Salaries & Contracts)
- **Status:** **BLOCKED**. Returns HTTP 403.
- **Decision:** Excluded from the active pipeline.

### 7. EA Sports FC / FIFA Ratings via Kaggle (Proxy Attributes)
- **Status:** **DEFERRED**. 
- **Decision:** While Kaggle datasets are legitimate, blending video game proxy attributes with real football statistics (from FPL) risks muddying the statistical integrity of the dataset. Deferred unless strictly necessary for future phases.
