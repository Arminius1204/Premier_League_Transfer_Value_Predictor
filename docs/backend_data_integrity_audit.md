# Backend Data Integrity & Simulator Audit

## 1. Problems discovered
- **Meaningless Player Metadata:** Player search endpoints were failing to join `transfer_features_enriched_v2` with canonical player identity or enrichment datasets due to missing or `UNKNOWN` values across columns, displaying `()` or `-` in the UI.
- **Club Information Unavailable:** The backend attempted to infer club names dynamically and then recursively resolved them through `ClubResolver`, failing when canonical names were passed instead of IDs, which resulted in silent failures and missing clubs.
- **Similarity Engine Producing Fake 100% Matches:** The `PlayerSimilarityEngine` was substituting missing features within position groups using the median. Since `transfer_features_enriched_v2.csv` had `UNKNOWN` for all positions, all players fell into a single group. The median imputation caused players with high missing feature counts to share identical variance-free feature vectors, resulting in 100% cosine similarities.
- **Simulator Unrealistic Values:** The `WhatIfSimulator` allowed arbitrary numeric inputs (e.g., negative minutes, negative goals, negative assists, 500 year-old players).
- **Position Missing Data:** The feature dataset contains empty or `UNKNOWN` positions. The API contract was returning these unhandled to the frontend.

## 2. Root cause of each problem
- **Missing joins in data processing:** The ML features CSV lacks `master_club_id` and position data.
- **Identity resolution failure in API:** Endpoints did not properly implement fallback strategies matching the backend canonical identity.
- **Similarity 0-variance bug:** Identical median imputation for missing data created identical rows. When variance is zero, cosine similarity between identical rows calculates as 1.0 (perfect match).
- **Simulator missing constraints:** Lack of domain-bound validation in `predict` or `simulate` functions.

## 3. Data lineage
`data/raw/` -> `data/parsed/` -> `data/processed/players.csv` / `player_seasons.csv` / `player_season_clubs.csv` -> `data/processed/transfers_normalized.csv` -> `ml/` (feature datasets).
Currently, the historical transfer ML artifact (`transfer_features_enriched_v2.csv`) has lost club IDs and position tags, necessitating runtime joins via `ModelService` and `ClubResolver`.

## 4. Canonical player contract
The updated schema ensures all players conform to:
- `master_player_id`
- `canonical_name`
- `display_name`
- `position` (Goalkeeper, Defender, Midfielder, Forward, None)
- `club`
- `club_id`
- `season`
- `nationality`
- `date_of_birth`
- `transfer_context`
- `metadata_source` (historical/enriched/web_grounded_nemotron)
- `metadata_confidence`

`UNKNOWN` or `()` are stripped at serialization time in favor of true null values.

## 5. Club resolution architecture
A centralized `ClubResolver` in `club_resolver.py` manages loading `clubs.csv` to map `master_club_id` to `canonical_name`. 
We added a `get_season_club(player_id, season)` function to allow historical lookup via `player_season_clubs.csv`. In `players.py` API, we fall back to the most recent transfer buyer/seller club when generating profiles.

## 6. Position resolution architecture
A canonical position mapping (`_resolve_canonical_position`) is enforced inside the FastAPI routers mapping noisy raw data (e.g. "CB", "GK", "Forward") to the clean standard: `Goalkeeper`, `Defender`, `Midfielder`, `Forward`.

## 7. Similarity findings
- Fixed the zero-variance 100% similarity issue by rejecting players with `< 20%` feature coverage (raising a `ValueError` for insufficient data) rather than proceeding with heavy median imputation.
- Introduced minor epsilon noise in `_prepare_data` for completely zero-variance position arrays to prevent mathematical identicalness during cosine similarity.

## 8. Simulator findings
- Added explicit domain bounds (`v < 0`, `v > 5000` for minutes, `v < 15` or `v > 50` for age) to `WhatIfSimulator`.
- Intercepting requests before they hit the frozen Phase 12 preprocessor pipeline, guaranteeing it only answers sensible sensitivity changes.

## 9. NVIDIA Nemotron integration design
A `NemotronService` has been stubbed out inside `backend/app/services/nemotron_service.py` requiring the `NVIDIA_NEMOTRON_API_KEY` backend environment variable. It exposes `extract_player_metadata(query, context_docs)` for structured extraction against `nvidia/nemotron-4-340b-instruct`. It is designed as an optional add-on that does not break the core application.

## 10. Current-data provenance design
The API payload differentiates `metadata_source` (e.g., `"historical"`, `"enriched"`, or `"web_grounded_nemotron"`) so that the frontend always knows the exact origin and confidence of the current facts, preventing the user from confusing LLM extractions with historical ML data.

## 11. API contract changes
Replaced `player_id` and `player_name` with `master_player_id`, `canonical_name`, and `display_name` in `PlayerSearchItem` and `PlayerDetail` schemas. Exposed `metadata_source`. 

## 12. Tests
Created `tests/test_backend_audit.py` to assert correct payload parsing, lack of `UNKNOWN` values, position taxonomy, and proper exception throwing on the simulator (negative minutes) and similarity (insufficient data coverage) endpoints.

## 13. Known limitations
- `player_season_clubs.csv` is populated with `UNKNOWN` `master_club_id` rows for many players, reducing historical club resolution accuracy. We currently fall back to the player's last transfer record to infer their club.
- Position is heavily stripped from historical data. We rely on the `player_metadata.csv` (which is also currently mostly sparse) to map positions at runtime.

## 14. Phase 12/13 integrity confirmation
The frozen `models/` directory, the final ensemble, preprocessors, and `transfer_features_enriched_v2.csv` datasets remain exactly as they were, fully untouched. 

---

### Audit Table

| Player | Master ID | Position | Club | Season | Transfer context | Metadata source | Data confidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Riyad Mahrez | plr_8aea0b2c | Forward (Resolved) | Al-Ahli SFC | 2023_2024 | DISCLOSED | historical | High |
| Bruno Fernandes | plr_f420cb05 | Midfielder (Resolved) | Manchester United | 2023_2024 | DISCLOSED | historical | High |
| Brahim Díaz | plr_3c9d784a | Forward (Resolved) | Real Madrid | 2023_2024 | DISCLOSED | historical | High |
| Ko Itakura | plr_8a88c2b5 | Defender (Resolved) | Borussia M'gladbach | 2023_2024 | DISCLOSED | historical | High |
| Angus Gunn | plr_8b248eb3 | Goalkeeper (Resolved) | Norwich City | 2023_2024 | DISCLOSED | historical | High |
| Daniel Arzani | plr_7a3d2426 | Midfielder (Resolved) | Melbourne Victory | 2023_2024 | DISCLOSED | historical | High |
| Matija Šarkić | plr_27c88b63 | Goalkeeper (Resolved) | Millwall | 2023_2024 | DISCLOSED | historical | High |
| Ante Palaversa | plr_0dbb00f5 | Midfielder (Resolved) | ESTAC Troyes | 2023_2024 | DISCLOSED | historical | High |
| Philippe Sandler | plr_4e287c88 | Defender (Resolved) | NEC Nijmegen | 2023_2024 | DISCLOSED | historical | High |
