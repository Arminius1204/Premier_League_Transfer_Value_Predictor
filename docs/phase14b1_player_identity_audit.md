# Phase 14B.1 — Player Identity & Metadata Audit

## Audit Date: 2026-09-30

---

## 1. Current Data State

### 1.1 `data/processed/players.csv`
- **Total players**: 4,799
- **Columns**: `master_player_id`, `canonical_name`, `date_of_birth`, `canonical_position`, `nationality`, `height`, `preferred_foot`, `created_at`
- **Issues**:
  - ALL `canonical_name` values are **lowercase** (e.g., `riyad mahrez`, `héctor bellerín`)
  - `date_of_birth`: ALL empty
  - `canonical_position`: ALL empty
  - `nationality`: ALL empty
  - `height`: ALL empty
  - `preferred_foot`: ALL empty
  - 590 names contain accented characters (stored correctly as UTF-8, but lowercase)

### 1.2 `data/processed/player_seasons.csv`
- **Total records**: 4,384
- **Columns**: `master_player_id`, `season_id`, `master_club_id`, `minutes`, `goals`, `assists`, `bps`
- **Issues**:
  - `master_club_id`: ALL values are `UNKNOWN`
  - Performance stats (minutes, goals, assists, bps) are populated correctly

### 1.3 `data/processed/player_season_clubs.csv`
- **Total records**: 4,384
- **Columns**: `master_player_id`, `season_id`, `master_club_id`
- **Issues**:
  - `master_club_id`: ALL values are `UNKNOWN`

### 1.4 `data/processed/clubs.csv`
- **Total clubs**: 29
- **Columns**: `master_club_id`, `canonical_name`, `country`, `league`
- **State**: Properly populated with correct club names (e.g., `club_b218207a` → `Manchester City`)
- **Note**: This data EXISTS but is never linked to players because `player_season_clubs.csv` has all `UNKNOWN` club IDs

### 1.5 `data/processed/transfers_normalized.csv`
- **Total records**: 2,831
- **Columns**: `transfer_id`, `master_player_id`, `season_id`, `transfer_date`, `from_club_id`, `to_club_id`, `fee_status`, etc.
- **Issues**:
  - `from_club_id`: ALL `UNKNOWN`
  - `to_club_id`: ALL `UNKNOWN`

### 1.6 `data/processed/transfer_features_enriched_v2.csv` (ML Feature File — FROZEN)
- **Total records**: 2,831
- **Key columns**: `master_player_id`, `season_id`, `position`, `fee_gbp`, plus 25+ engineered features
- **Issues**:
  - `position`: ALL values are `UNKNOWN`
- **Status**: This file is the ML training data and MUST NOT be modified

### 1.7 `data/entity_resolution/player_identity_map.csv`
- **Total records**: 7,627
- **Unique players**: 4,799
- **Sources**: FPL (4,383 records), Transfermarkt (3,244 records)
- **Columns**: `master_player_id`, `source`, `source_player_id`, `source_player_name`, `source_club_id`, `source_club_name`, `season_id`, `match_confidence`, `match_method`, `review_status`
- **State**:
  - `source_player_name`: **Properly capitalized with Unicode preserved** (e.g., `Riyad Mahrez`, `Héctor Bellerín`, `Mesut Özil`)
  - `source_player_id`: 1,535 Transfermarkt IDs populated (numeric IDs like `171424`)
  - `source_club_id`: ALL empty/NaN
  - `source_club_name`: ALL empty/NaN
  - `match_confidence`: 100.0 for all records
  - `review_status`: ALL `APPROVED`

---

## 2. Root Cause Analysis

### Why are names lowercase?
The `data/processed/players.csv` canonical_name was stored in lowercase during the warehouse build phase (`ml/warehouse/build_warehouse.py`). The identity resolution step (`ml/entity_resolution/player_resolver.py`) correctly maps to properly cased source names, but the canonical_name in players.csv was never updated from its initial lowercase form.

### Why are positions UNKNOWN?
The position field in `transfer_features_enriched_v2.csv` is `UNKNOWN` because the warehouse builder could not resolve positions from the available data sources. FPL data has position codes (1=GK, 2=DEF, 3=MID, 4=FWD) but these were not mapped during feature engineering.

### Why are clubs UNKNOWN?
The club resolution step either failed or was never connected. `clubs.csv` has 29 properly named clubs, but `player_season_clubs.csv` has all `UNKNOWN` master_club_ids, meaning the join between player-season records and clubs never succeeded in the warehouse build.

### Why is "Unknown Club" displayed?
The frontend `frontend/app/players/[id]/page.tsx` line 72 renders:
```tsx
{detail.clubs[detail.clubs.length - 1] || "Unknown Club"}
```
Since `model_service.py` reads clubs from the `club` column of the ML feature DataFrame (which doesn't exist), it returns an empty array, triggering the fallback.

### Why is there no player image?
No image/photo data has ever been collected. No external API integration exists for player images.

---

## 3. Available Data for Enrichment

| Source | Players | Canonical Names | External IDs | Positions | Clubs | Photos |
|--------|---------|-----------------|--------------|-----------|-------|--------|
| FPL Identity Map | 4,383 | ✅ Proper case | FPL slugs | ❌ | ❌ | ❌ |
| Transfermarkt Identity Map | 1,535 | ✅ Proper case | ✅ TM IDs | ❌ | ❌ | ❌ |
| clubs.csv | — | — | — | — | ✅ 29 clubs | — |
| API-Football | — | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 4. Current API Response Issues

### Search endpoint (`GET /players`)
```json
{
  "player_id": "plr_8aea0b2c",
  "player_name": "riyad mahrez",     // ← lowercase
  "position": "UNKNOWN"               // ← raw UNKNOWN string
}
```

### Detail endpoint (`GET /players/{id}`)
```json
{
  "player_id": "plr_8aea0b2c",
  "player_name": "riyad mahrez",     // ← lowercase
  "position": "UNKNOWN",              // ← raw UNKNOWN
  "seasons": ["2018_2019"],
  "clubs": [],                         // ← empty (no club column in ML DataFrame)
  "transfer_history": [...]
}
```
- No `photo_url`
- No `nationality`
- No `date_of_birth`

---

## 5. Enrichment Plan

### Phase 1: Identity Map Extraction (No external API needed)
- Extract canonical names from identity map (Transfermarkt preferred, FPL fallback)
- Create `data/player_enrichment/player_metadata.csv`
- Coverage: 100% of 4,799 players get canonical names

### Phase 2: API-Football Enrichment (Requires API key)
- Match players by Transfermarkt ID or name
- Enrich: position, nationality, date_of_birth, photo_url
- Deterministic matching hierarchy with confidence tracking
- Unresolved players go to review queue

### Phase 3: Backend Integration
- Enrichment service loads metadata at startup
- Player routes merge enrichment data into responses
- Club resolver maps club IDs to names
- All new fields are Optional (backward compatible)

### Phase 4: Frontend Integration
- Display canonical names from API
- Show player photos with next/image
- Fallback placeholder for missing photos
- Position/club/nationality display

---

## 6. Files to Create/Modify

### New Files
- `data/player_enrichment/player_metadata.csv`
- `data/player_enrichment/review_queue.csv`
- `backend/app/services/enrichment_service.py`
- `backend/app/services/api_football_client.py`
- `backend/app/services/club_resolver.py`
- `scripts/enrich_players.py`
- `tests/test_enrichment.py`
- `frontend/components/ui/PlayerImage.tsx`
- `docs/phase14b1_player_identity_report.md`

### Modified Files
- `backend/app/config.py` — Add enrichment config
- `backend/app/dependencies.py` — Add enrichment dependency
- `backend/app/schemas/player.py` — Add optional enrichment fields
- `backend/app/api/routes/players.py` — Merge enrichment data
- `backend/app/services/model_service.py` — Add club resolution
- `frontend/lib/api/types.ts` — Add photo_url, nationality, club fields
- `frontend/app/players/page.tsx` — Show player images
- `frontend/app/players/[id]/page.tsx` — Show enriched profile
- `frontend/app/compare/page.tsx` — Show player thumbnails
- `frontend/next.config.ts` — Add image domains

### NOT Modified (ML Core Frozen)
- `ml/` — All files unchanged
- `models/` — All artifacts unchanged
- `data/processed/transfer_features_enriched_v2.csv` — Unchanged
- `tests/test_modeling*.py` — Unchanged
- `tests/test_phase13.py` — Unchanged
