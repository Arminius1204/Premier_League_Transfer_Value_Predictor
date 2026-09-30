# Player Repetition Audit

- **Total Transfer Events:** 371
- **Unique Players:** 205
- **Repeated Players (multiple transfers):** 152

## Temporal Leakage Implications
Because we are using Walk-Forward Validation, a player appearing in Train (e.g., a transfer in 2021) and Test (e.g., a transfer in 2023) is conceptually valid because their 2023 valuation reflects new historical information. However, to prevent the model from memorizing individual identities, **master_player_id** MUST NOT be used as a predictor.
