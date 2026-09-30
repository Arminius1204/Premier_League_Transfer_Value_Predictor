# Data Acquisition Phase

## Overview
This document outlines the exact mechanisms used to acquire raw data for the Premier League Transfer Intelligence project. The golden rule of this phase is **reproducibility** and **respect for source systems**. 

### Principles
1. **No Silent Failures:** All HTTP errors (e.g., 403, 429, 404) are logged.
2. **Raw Preservation:** Downloaded HTML, JSON, and CSV files are stored exactly as received in `/data/raw/<source>/`. No cleaning or transformation is performed during acquisition.
3. **Metadata Enrichment:** Every downloaded file is paired with a `.meta.json` file recording the source, retrieval timestamp, size, and target season.
4. **Respect Restrictions:** We adhere strictly to rate limits (e.g., 5 seconds between FBref requests) and do not bypass anti-bot challenges (e.g., Transfermarkt Cloudflare blocks).

## Data Collectors

### 1. `match_data.py` (football-data.co.uk)
- **Endpoint:** `https://www.football-data.co.uk/mmz4281/{season}/E0.csv`
- **Method:** GET
- **Format:** CSV
- **Rate Limit:** 1.0 sec
- **Behavior:** Downloads full season match result CSVs. Highly reliable.

### 2. `advanced_stats.py` (Understat)
- **Endpoint:** `https://understat.com/league/EPL/{season}`
- **Method:** GET
- **Format:** HTML (contains embedded JSON payloads)
- **Rate Limit:** 3.0 sec
- **Behavior:** Downloads the full HTML payload for later JSON extraction of player/team xG stats.

### 3. `premier_league_stats.py` (FBref)
- **Endpoint:** `https://fbref.com/en/comps/9/{season}/{season}-Premier-League-Stats`
- **Method:** GET
- **Format:** HTML
- **Rate Limit:** 5.0 sec
- **Behavior:** Strictly respects the 20 requests/minute rule. Dumps the HTML page containing standard and advanced Opta stats tables.

### 4. `transfer_data.py` (Transfermarkt)
- **Endpoint:** `https://www.transfermarkt.com/premier-league/transfers/wettbewerb/GB1/plus/?saison_id={season}`
- **Method:** GET
- **Format:** HTML
- **Rate Limit:** 5.0 sec
- **Behavior:** Often blocked by Cloudflare (403 Forbidden). We do not use proxies or headless browsers to bypass this. When blocked, the collector logs the error and gracefully skips, leaving a documented missing data gap.
