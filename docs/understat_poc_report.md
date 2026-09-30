# Understat Player-Level POC & Scale Report

## 1. Execution Attempt
Following the architecture plan, a direct HTTP request was made to `https://understat.com/team/Arsenal/2023` to extract the `playersData` JSON payload.

## 2. Result: BLOCKED
*   **Payload Size:** 19 KB (Expected: > 500 KB).
*   **Data Presence:** Neither `teamsData` nor `playersData` exists in the DOM.
*   **Root Cause:** Understat has implemented strict Cloudflare/anti-bot protection that serves a headless shell or challenge page to Python `requests`. 
*   *(Note: This retroactively confirms that our Phase 4 Understat league-level extractions also received 19 KB empty shells, explaining the parser failures).*

## 3. Compliance with Project Constraints
The explicit project mandate states:
> *"Do NOT bypass: Cloudflare, CAPTCHA, robots restrictions, anti-bot systems, access controls... If the team-page approach fails or access becomes restricted: STOP. Document the limitation. Do not bypass it."*

In strict adherence to these rules, no headless browsers (Selenium/Playwright) or proxy-rotation mechanisms were employed to spoof browser fingerprints. 

## 4. Status Update
**UNDERSTAT is officially classified as BLOCKED.**
We will not scale the extraction. The absence of Understat, combined with the earlier blocks on FBref and Capology, means we legally cannot acquire historical, multi-season advanced player performance (xG, xA, key passes) via our automated pipeline.

## 5. Alternative Strategy for ML Feasibility
Without FPL history or Understat/FBref, we do not have granular per-90 metrics (goals, assists, xG) for `2021/22` and `2022/23`. 
To preserve a scientifically defensible model, we will pivot our feature engineering to rely on robust, legally acquired data:
1.  **Player Demographics:** Age, Position, Nationality (available via Transfermarkt tables).
2.  **Club-Level Performance:** Selling club points, goals, and league position for season T-1 (fully captured via `football-data.co.uk`).
3.  **Transfer Context:** Transfer window timing and buying-club prestige.

This ensures the model remains mathematically viable, albeit focusing on demographic and club-context valuation rather than granular on-ball performance.
