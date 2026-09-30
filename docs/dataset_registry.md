# Dataset Registry

This registry tracks the publicly accessible and legally usable sources that will form the ecosystem of the Premier League Transfer Intelligence & Player Valuation Engine.

## Core Data Sources

### 1. Transfermarkt (Market & Transfer Data)
- **URL:** https://www.transfermarkt.com
- **API Availability:** Unofficial APIs (e.g., `transfermarkt-api` node wrappers) or direct BeautifulSoup/requests scraping.
- **Python `requests` Compatibility:** High, but requires custom User-Agent headers and strict rate-limiting (e.g., `time.sleep(2)`) to avoid IP bans.
- **Seasons Covered:** 1992 - Present (Premier League era).
- **Data Granularity:** Player-level, Transfer-level (event), Club-level.
- **Important Fields:** `transfer_fee_eur`, `market_value`, `contract_expiry`, `date_of_birth`, `nationality`, `position`, `joined_club`.
- **Licensing/Restrictions:** Academic/Research is generally tolerated under fair use via scraping. Commercial use requires a paid license/API agreement with Transfermarkt.
- **Join Keys:** `player_name`, `date_of_birth`, `club`, `season`.
- **Intended Purpose:** The ultimate source for our target variable (Transfer Fee), as well as player demographics, contract length, and historical transfer events.

### 2. FBref via Opta (Performance Data)
- **URL:** https://fbref.com
- **API Availability:** Standard HTML scraping. Libraries like `soccerdata` and `worldfootballR` are highly recommended.
- **Python `requests` Compatibility:** Very strict rate-limiting. FBref imposes a maximum of 20 requests per minute. `429 Too Many Requests` will result in an hour-long ban.
- **Seasons Covered:** 1992 - Present. (Note: Advanced Opta data like xG, xA, and pressures are only available from 2017/18 onwards).
- **Data Granularity:** Player-season, Player-match.
- **Important Fields:** `minutes_played`, `xG`, `xA`, `shot_creating_actions`, `progressive_passes`, `tackles_interceptions`, `aerials_won`.
- **Licensing/Restrictions:** Sports Reference Data Use Policy. Non-commercial scraping is allowed with proper attribution. Commercial use is prohibited.
- **Join Keys:** `player_name`, `club`, `season`.
- **Intended Purpose:** Core feature set for ML modeling. Provides all advanced attacking, passing, and defensive statistics per 90 minutes.

### 3. Understat (Expected Goals & Shot Data)
- **URL:** https://understat.com
- **API Availability:** None officially, but the data is embedded as JSON inside `<script>` tags in the HTML.
- **Python `requests` Compatibility:** Extremely compatible; parsing the JSON payload via regex/BeautifulSoup is standard practice.
- **Seasons Covered:** 2014 - Present.
- **Data Granularity:** Match-level, Shot-level, Player-match.
- **Important Fields:** `xG`, `xA`, `key_passes`, `shot_type`, `situation` (Open play, Set piece).
- **Licensing/Restrictions:** Fair use for academic/personal projects. 
- **Join Keys:** `player_name`, `club`, `season`.
- **Intended Purpose:** Granular, specialized attacking data. Useful for validating FBref xG and diving deeper into attacker performance profiles.

### 4. football-data.co.uk (Match Context & Club Form)
- **URL:** https://www.football-data.co.uk/englandm.php
- **API Availability:** Direct CSV downloads per league/season.
- **Python `requests` Compatibility:** 100% compatible. Fast static file downloads.
- **Seasons Covered:** 1993 - Present.
- **Data Granularity:** Match-level.
- **Important Fields:** `HomeTeam`, `AwayTeam`, `FTHG` (Full Time Home Goals), `FTAG`, `Referee`, `B365H` (Betting Odds).
- **Licensing/Restrictions:** Free to use, including commercially.
- **Join Keys:** `club`, `match_date`, `season`.
- **Intended Purpose:** Contextual club data. Used to calculate team form (last 5 games), Elo ratings, league standings at the time of transfer, and club prestige.

### 5. EA Sports FC / FIFA Ratings via Kaggle (Proxy/Scouting Attributes)
- **URL:** https://www.kaggle.com/datasets
- **API Availability:** Kaggle API.
- **Python `requests` Compatibility:** via `kaggle` python package.
- **Seasons Covered:** FIFA 15 to FC 24 (Approx. 2014 - 2023).
- **Data Granularity:** Player-season.
- **Important Fields:** `overall`, `potential`, `pace`, `physic`, `weak_foot`, `skill_moves`.
- **Licensing/Restrictions:** Kaggle CC0 or fair-use depending on the uploader. Commercial use of EA intellectual property is prohibited.
- **Join Keys:** `player_name`, `club`, `season`.
## Expanded Data Sources (FBref Alternatives & Supplements)

Because FBref actively blocks automated requests with HTTP 403 (Anti-Bot), we require alternative sources that provide overlapping player statistics to ensure system redundancy.

### 6. Fantasy Premier League (FPL) API
- **URL:** `https://fantasy.premierleague.com/api/bootstrap-static/`
- **API Availability:** Official JSON API.
- **Python `requests` Compatibility:** Excellent. Fully accessible without strict anti-bot mechanisms.
- **Seasons Covered:** Current season (historical seasons require using community archives like the FPL Historical Dataset repo).
- **Data Granularity:** Player-season, Player-match.
- **Important Fields:** `goals_scored`, `assists`, `minutes`, `expected_goals`, `expected_assists`, `bps` (Bonus Points System - a proxy for overall match performance).
- **Licensing/Restrictions:** Free for personal/academic use.
- **Join Keys:** `player_name`, `club_name`, `season_id`.
- **Intended Purpose:** Primary backup for player performance metrics and xG.

### 7. FotMob API (Unofficial)
- **URL:** `https://www.fotmob.com/api/`
- **API Availability:** Unofficial JSON endpoints used by their frontend.
- **Python `requests` Compatibility:** Very high, standard requests with headers work well.
- **Seasons Covered:** Historically deep (typically 2010+).
- **Data Granularity:** Player-season, Match-level.
- **Important Fields:** `player_id`, `rating` (Algorithmic match ratings), `goals`, `assists`, `chances_created`.
- **Licensing/Restrictions:** Web scraping for personal/academic use.
- **Join Keys:** `player_name`, `club_name`, `season_id`.
- **Intended Purpose:** Secondary backup for match ratings and granular performance stats. 

### 8. Capology (Salaries & Contracts)
- **URL:** `https://www.capology.com/`
- **API Availability:** HTML scraping.
- **Python `requests` Compatibility:** High, requires standard headers.
- **Seasons Covered:** ~2015 - Present.
- **Data Granularity:** Player-season.
- **Important Fields:** `weekly_wage`, `annual_wage`, `contract_length`, `expiration_date`.
- **Intended Purpose:** Contract data is heavily correlated with transfer value. Used as a supplementary dataset to enrich Transfermarkt data.
