# Phase 15N: V4 Leakage-Free Transfer-Fee Model Card

## 1. Model Details
- **Model Name:** V4 Leakage-Free Transfer-Fee Regressor
- **Architecture:** Random Forest Regressor (`n_estimators=200`, `max_depth=10`)
- **Target:** `log_fee_gbp`
- **Objective:** Predict historical real-world transfer fees in the Premier League exclusively using historical performance context available *before* the transfer occurred.

## 2. Intended Use
- **Primary Use:** Backend simulation and "What-If" market valuations based on pure performance indicators, immune to post-transfer market valuations or media-hype leakage.
- **Out of Scope:** V4 is NOT intended to perfectly replicate £100m+ transfers, as those are heavily influenced by commercial factors not currently captured in the restricted Phase 15 feature space.

## 3. Training Data & Feature Set
V4 strictly utilizes a pre-transfer subset of features. The dataset was rebuilt in Phase 15C to remove `market_value` entirely.

**Included Features:**
- `t1_minutes`: Premier League / Foreign T-1 minutes played (median imputed if foreign)
- `t1_goals`: T-1 goals scored
- `t1_assists`: T-1 assists
- `is_foreign_import`: Binary flag denoting missing FPL history (0 for domestic, 1 for foreign imports)
- `previous_transfer_count`: Historical transfer frequency
- `career_minutes_before_transfer`: Accumulation of all pre-transfer recorded minutes
- `career_goals_before_transfer`: Accumulation of all pre-transfer goals
- `position`: Categorical player position
- `is_summer_window`: Binary seasonality flag

**Excluded Features:**
- `market_value`: Dropped due to extreme target leakage (post-transfer valuations).
- `age_at_transfer`: Dropped due to 100% missingness resulting from unmapped `date_of_birth` in FPL data.
- `selling_club_pts_t1`: Dropped due to incomplete club entity resolution between Transfermarkt and FPL.

## 4. Performance Metrics (Chronological Test Set)
The model was evaluated using an 80/20 chronological split, predicting forward in time.

- **R² Score:** 0.0710 
- **Overall MAE:** £13.65m
- **High-Value Transfer MAE (>£50m):** £52.82m

### 4.1 Erling Haaland Target Consistency Test
- **Actual Transfer Fee:** £51,540,000
- **V3 Prediction (Flawed T-1 mapping):** £14.5M
- **V4 Candidate Prediction (No Leakage, Fixed T-1 mapping):** £27,437,078
- **Absolute Error (V4):** £24,102,921

## 5. Deployment Recommendation
**DO NOT DEPLOY V4 AS THE PRIMARY VALUATION ENDPOINT YET.**

While V4 successfully eliminates target leakage and utilizes repaired historical statistics (e.g., Haaland's 22 T-1 goals), the R² score (0.0710) confirms that the restricted feature set is currently insufficient to act as a highly accurate standalone predictor for public display.

**Next Steps (Phase 16 - Data Expansion):**
1. Re-integrate demographic data (`age_at_transfer`) by fixing Transfermarkt parsing to capture Date of Birth.
2. Re-integrate contextual club data (`selling_club_pts_t1`) by normalizing foreign club IDs.
3. Deploy V4 purely as a secondary "Performance-Only Value Proxy" endpoint while the primary model is rebuilt with expanded data.
