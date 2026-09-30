# Temporal Leakage Policy

Data leakage is the most critical threat to a transfer-valuation model. This policy defines exactly how predictor features are aligned relative to the transfer event (`T`).

## The Core Axiom
For every transfer event at `transfer_date = T`, any predictor used by the model must satisfy:
`information_timestamp < T`

## Temporal Linkage Mapping
The warehouse generates `transfer_performance_links.csv` to explicitly bridge transfer events to their latest valid performance season.
*   *Summer Transfers (e.g., July 2023):* Mapped directly to the completed previous season (e.g., `2022_2023`). 
*   *Winter Transfers (e.g., January 2024):* (Pending detailed extraction). Can use `2022_2023` (previous completed season) + partial aggregated data up to December 31, 2023 (requires match-by-match timeline data, which we have not yet parsed at the player level).

## Categorical Validity Statuses
Features are explicitly flagged in `feature_temporal_validity.csv` using:
1.  **VALID:** Information strictly precedes the transfer. (e.g., `previous_season_goals`).
2.  **INVALID:** Information spans past the transfer. (e.g., `current_season_goals`).
3.  **REQUIRES_ALIGNMENT:** Information whose timestamp is ambiguous or constantly retroactively updated (e.g., `Transfermarkt Current Market Value`).

*Crucial Restriction on FPL Data:* FPL "now_cost" is strictly an artifact of the game at the time of data download and cannot be reliably reconstructed as historical transfer-market information. It is heavily leakage-prone and must be excluded from modeling transfer fees.
