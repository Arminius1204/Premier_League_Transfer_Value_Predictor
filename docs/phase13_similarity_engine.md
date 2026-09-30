# Phase 13 Similarity Engine

## 1. Objective
Build a reusable engine that determines historically comparable players based *exclusively on football performance and demographic profiles*. Transfer price is strictly isolated from this calculation to prevent tautological reasoning (i.e. "they are similar because they cost the same").

## 2. Feature Selection
The engine uses a curated subset of the Phase 12 enriched feature set.

| Feature | Used? | Reason |
| :--- | :--- | :--- |
| `age_at_transfer` | **Yes** | Age profoundly dictates career stage and trajectory. |
| `position` | **Filter** | Position compatibility is enforced (e.g. Forwards are compared to Forwards). |
| `t1_minutes` | **Yes** | Indicates player availability and durability prior to transfer. |
| `t1_goals_per90` | **Yes** | Primary attacking output normalized for playtime. |
| `t1_assists_per90` | **Yes** | Primary creative output normalized for playtime. |
| `t1_bps_per90` | **Yes** | Proxies overall underlying contribution (tackles, passes, saves). |
| `career_minutes_before_transfer` | **Yes** | Distinguishes veterans from unproven prospects. |
| `selling_club_pts_t1` | **Yes** | Contextualizes whether the player thrived in a dominant or struggling team. |
| `fee_gbp` / `log_fee_gbp` | **NO** | Target variable/market price. |
| `master_player_id` | **NO** | Prevents arbitrary identity memorization. |
| `transfer_id` | **NO** | Metadata. |

## 3. Position-Aware Methodology
1.  **Strict Filtering:** When a player's similarity is queried, the historical dataset is strictly filtered to players matching their canonical position (`GOALKEEPER`, `DEFENDER`, `MIDFIELDER`, `FORWARD`).
2.  **Missing Data Imputation:** Sparse statistics (e.g., a player lacking FPL history) are median-imputed *within that position group* to prevent extreme distortions (e.g., zeroing out goals for a defender vs a forward).
3.  **Standardization:** Continuous features are rescaled using `StandardScaler` so that `age` (range 15-40) and `t1_minutes` (range 0-3420) carry proportional vector weights.
4.  **Cosine Similarity:** The dot product of the standardized vectors is calculated, yielding a bounded score from -1 to 1 (where 1 is identical).

## 4. Modes Supported
*   **Player -> Players:** Provide a `master_player_id` and `season_id`, returns Top K historical peers.
*   **Profile -> Dataset:** Provide a theoretical dictionary (e.g., 22yo Forward with 0.6 Goals/90), returns Top K historical peers.
*   **Player -> Player:** Directly calculate the Cosine distance between two named individuals in specific seasons.

## 5. Output and Transparency
The engine explicitly logs:
*   `Similarity Score` (e.g., 0.94)
*   `Feature Coverage` (e.g., 8/8 data points available)
*   `Historical Transfer Fee` (Appended post-calculation strictly for analytical context).
