# Data Source Evaluation & Risk Analysis

This document evaluates the quality, risks, and feasibility of the chosen datasets for the Premier League Valuation Engine.

## 1. Transfermarkt (Market Values & Transfers)
- **Data Quality:** Excellent for historical records (who moved where, when).
- **Missing Data Risks:** 
  - **Undisclosed Fees:** Many transfers are officially "Undisclosed". Transfermarkt provides estimates based on media reports. *Mitigation:* We must flag estimated fees vs. official fees and potentially exclude loans or free transfers from the regression modeling.
  - **Contract Lengths:** Historical contract data pre-2015 is often spotty.
- **Usage Feasibility:** Scraping is heavily rate-limited. We must use deliberate, slow scraping tactics, caching all HTML locally so we don't request the same page twice.

## 2. FBref (Performance Statistics)
- **Data Quality:** Gold standard (backed by Opta).
- **Missing Data Risks:** 
  - **The Opta Era Divide:** Advanced stats (xG, xA, pressures, progressive passes) only exist for the Premier League from the 2017/2018 season onwards.
  - *Mitigation:* We will likely need two models or a specialized pipeline. Model A uses basic stats (goals, assists, minutes) for all data 1992-Present. Model B uses advanced stats but is restricted to post-2017 transfers.
- **Usage Feasibility:** Strict 20 requests/minute limit. We will implement robust API backoff strategies and use bulk CSV dumps where available.

## 3. Understat (Shot-Level xG)
- **Data Quality:** High, though xG models differ slightly from Opta's model.
- **Missing Data Risks:** Only covers league matches (no cup games). Not available before 2014.
- **Usage Feasibility:** Very easy to extract via Python JSON parsing from script tags. Low risk of blocking.

## 4. football-data.co.uk (Match Results)
- **Data Quality:** Extremely reliable.
- **Missing Data Risks:** None. Fully complete CSVs.
- **Usage Feasibility:** Immediate download. The only challenge is mapping club names (e.g., "Nott'm Forest" vs "Nottingham Forest"). We will create a static `club_name_mapping.json`.

## 5. EA Sports FIFA Datasets (Attributes proxy)
- **Data Quality:** Subjective. Represents EA scouts' opinions rather than strict statistical reality.
- **Missing Data Risks:** Players who break through mid-season might not have a rating until the next game iteration. 
- **Usage Feasibility:** Easily downloaded from Kaggle. Excellent for generating "Player Styles" (e.g., "Pacey Winger", "Target Man") via clustering.

## Strategic Conclusion
The combination of these 5 sources fulfills all project requirements. 
- **Transfermarkt** provides the *Target* (Price/Value).
- **FBref + Understat** provide the *Features* (What they did on the pitch).
- **football-data.co.uk** provides the *Context* (How good the team was).
- **FIFA Data** provides the *Scouting Profile* (Intangibles).

The primary technical hurdle is the **Entity Resolution (Join Map)** which we will address via fuzzy name matching + birth year cross-referencing.
