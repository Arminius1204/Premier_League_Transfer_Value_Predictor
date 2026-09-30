# Feature Dictionary

## A. PLAYER DEMOGRAPHICS
| feature_name | description | source | source_field | unit | aggregation | observation_period | available_before_transfer | temporal_rule | missing_value_strategy | leakage_risk | feature_group |
|--------------|-------------|--------|--------------|------|-------------|--------------------|---------------------------|---------------|------------------------|--------------|---------------|
| `age_at_transfer` | Player's age at the time of transfer | Transfermarkt | Age | Years | None | At Transfer | TRUE | Based on transfer date | Preserve as NULL | LOW | Demographics |
| `age_squared` | Polynomial term for age | Derived | - | Years^2 | None | At Transfer | TRUE | Based on transfer date | Preserve as NULL | LOW | Demographics |
| `position` | Normalized positional group | Transfermarkt | Position | Categorical | Hierarchy Mapping | At Transfer | TRUE | Based on TM profile at time | Map to UNKNOWN | LOW | Demographics |
| `nationality` | Primary nationality of the player | Transfermarkt | Nationality | Categorical | None | At Transfer | TRUE | Extracted from badge | Map to UNKNOWN | LOW | Demographics |

## B. CLUB CONTEXT (SELLING CLUB)
| feature_name | description | source | source_field | unit | aggregation | observation_period | available_before_transfer | temporal_rule | missing_value_strategy | leakage_risk | feature_group |
|--------------|-------------|--------|--------------|------|-------------|--------------------|---------------------------|---------------|------------------------|--------------|---------------|
| `prev_season_points` | Points accrued by selling club in T-1 | football-data | pts | Points | Season Total | T-1 Season | TRUE | Only uses T-1 completed standings | Preserve as NULL | LOW | Club Context |
| `prev_season_points_per_match` | Points per match by selling club in T-1 | Derived | - | Pts/Match | Season Avg | T-1 Season | TRUE | Only uses T-1 completed standings | Preserve as NULL | LOW | Club Context |
| `prev_season_gd` | Goal difference of selling club in T-1 | football-data | FTHG, FTAG | Goals | Season Total | T-1 Season | TRUE | Only uses T-1 completed standings | Preserve as NULL | LOW | Club Context |

## C. PLAYER PERFORMANCE
| feature_name | description | source | source_field | unit | aggregation | observation_period | available_before_transfer | temporal_rule | missing_value_strategy | leakage_risk | feature_group |
|--------------|-------------|--------|--------------|------|-------------|--------------------|---------------------------|---------------|------------------------|--------------|---------------|
| `prev_season_minutes` | Minutes played in T-1 season | FPL | minutes | Mins | Season Total | T-1 Season | TRUE | Only uses T-1 | Preserve as NULL | LOW | Performance |
| `low_minutes_flag` | Flag indicating if player played <450 mins | Derived | minutes | Binary | None | T-1 Season | TRUE | Only uses T-1 | Preserve as UNKNOWN | LOW | Performance |
| `prev_season_goals_per90` | Goals scored per 90 mins in T-1 | Derived | goals | Goals/90 | Season Avg | T-1 Season | TRUE | Only uses T-1 | Preserve as NULL | LOW | Efficiency |
| `prev_season_xg_per90` | Expected goals per 90 mins in T-1 | Derived | expected_goals | xG/90 | Season Avg | T-1 Season | TRUE | Only uses T-1 | Preserve as NULL | LOW | Efficiency |

## Target Variable
| feature_name | description | source | temporal_rule |
|--------------|-------------|--------|---------------|
| `fee_gbp` | Exact disclosed transfer fee in GBP | Transfermarkt | Explicitly target (do not use as feature) |
| `log_fee_gbp` | Natural log of fee_gbp + 1 | Derived | Target transformation |
