# Phase 9 Data Expansion Plan

## Historical Seasons Target
- 2018/19
- 2019/20
- 2020/21
- 2021/22
- 2022/23
- 2023/24

## Source Targets and Coverage
1. **Transfermarkt (CORE)**
   - Coverage: Transfer events, demographics (age, position, nationality), fees.
   - Status: Raw HTML successfully fetched and verified for all 6 target seasons.
   - Quality: High. Preserves fee text, date, and source IDs.

2. **football-data.co.uk (CORE)**
   - Coverage: Match results, team points, goal difference.
   - Status: CSVs successfully fetched for all 6 target seasons.
   - Quality: High. Clean structural format.

3. **Vaastav FPL Historical Archive (SUPPORTING)**
   - Coverage: Player performance per season (minutes, goals, assists, bonus points, creativity).
   - Status: Fetching from verified GitHub archive (publicly accessible, clear provenance).
   - Quality: High. Represents actual playing performance per season. Contains `first_name` and `second_name` for entity resolution.

4. **EA FC / FIFA Data (OPTIONAL)**
   - Coverage: Overall player rating proxies.
   - Status: Deferred unless FPL matching yields critically low coverage, as the project prioritizes real football statistics over video game attributes.

## Processing Strategy
1. Run parsing pipeline on new raw files.
2. Execute massive Entity Resolution across FPL and Transfermarkt for 6 seasons.
3. Track and isolate any statistical conflicts across sources.
4. Establish precise Temporal Validity (e.g. 2019/20 stats only valid for transfers occurring after July 2020).
