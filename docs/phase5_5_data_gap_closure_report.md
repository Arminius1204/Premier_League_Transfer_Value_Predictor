# Phase 5.5 Data Gap Closure Report

## 1. Initial Coverage Audit (Pre-Gap Closure)
Before this phase, we established that while we have 1,300 extracted transfer events (371 successfully parsing as `DISCLOSED` numeric target eligible), **0%** of these were usable for ML modeling under our strict temporal leakage policy. This was because FPL data only covers `2023/24`, meaning we had no historical performance features (e.g. `2022/23` data) to map to a `2023/24` transfer.

## 2. Understat Player-Level Architecture & Blocking (POC Results)
To resolve the player-level historical data gap, we attempted an architectural proof-of-concept (POC) to traverse the Understat tree: `League -> Team -> Player`. 
*   **Result:** BLOCKED.
*   **Details:** The `requests.get` call to `https://understat.com/team/Arsenal/2023` returned a 19 KB shell page containing no `teamsData` or `playersData`. Cloudflare/anti-bot protection actively blocks non-browser payloads.
*   **Compliance:** In strict compliance with the project rule *"Do NOT bypass: Cloudflare, CAPTCHA, robots restrictions... If access becomes restricted: STOP. Document the limitation,"* we abandoned the Understat scraper.

## 3. Revised Feature Strategy
Because Understat, FBref, and Capology are officially restricted, acquiring advanced on-ball metrics (xG, xA, key passes) across multiple historical seasons is impossible via automated scraping.
Instead, we pivot our feature engineering focus to available, legal datasets:
*   **Demographic Context (Transfermarkt):** Age, Position, Nationality.
*   **Selling Club Context (football-data.co.uk):** Previous season points, goals scored, goals conceded, league standing.
*   **Transfer Context:** Summer vs Winter window.

## 4. Historical FX Methodology
*   We audited the target eligible transfer currencies. `EUR` was the dominant currency.
*   **Methodology:** Since we lack an automated daily FX API, we utilized static, historically accurate mid-market exchange rates (July 1st) to normalize `EUR` to `GBP`.
*   **Rates Used:** 
    *   2021: 0.858
    *   2022: 0.859
    *   2023: 0.859
*   The warehouse (`build_warehouse.py`) now dynamically calculates and stores `fee_gbp` based on the transfer season.

## 5. Target-Eligible Sample Size (Final)
*   **Total Transfers Tracked:** 1,300
*   **Target Eligible (DISCLOSED numeric fees):** 371
*   **Breakdown by Season:**
    *   2021/22: 26
    *   2022/23: 43
    *   2023/24: 302
*   **Usable Observations:** With the pivot to Club-Context and Demographic features, all 371 of these target-eligible transfers can be matched to valid `T-1` data (from `football-data.co.uk` and TM).

## 6. Source Classification
*   **Transfermarkt:** CORE (Target variables, Demographics)
*   **football-data.co.uk:** CORE (Selling/Buying club context, T-1 performance)
*   **FPL:** SUPPORTING (Can provide performance context for the 23/24 subset)
*   **Understat:** BLOCKED
*   **FBref:** BLOCKED
*   **Capology:** BLOCKED

## 7. Next-Phase Prerequisites
With the data limits mapped, we are ready to proceed to Feature Engineering. We will construct a matrix utilizing `fee_gbp` as the target, supported by strictly pre-transfer (T-1) club context and demographic variables. 

---
**PHASE 5.5 STATUS:** PASS
*(Historical FX strategy successfully resolved. Understat strictly validated as blocked without bypassing anti-bot measures. Target-eligible sample size accurately quantified. Existing warehouse remains intact and data lineage updated).*
