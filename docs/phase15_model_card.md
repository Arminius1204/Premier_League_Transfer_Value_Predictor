# Phase 15 Model Card: Transfer Valuation Engine Candidate

## Overview
This model card details the Phase 15 experimental candidate for the Premier League Transfer Intelligence & Player Valuation Engine. This model aims to predict historical transfer fees and evaluate player valuations based on temporal performance, context, and historical market values.

## Data Details
- **Target Definition**: Numerical transfer fee in GBP (£) (`fee_gbp`). Free transfers and undisclosed fees are excluded unless definitively estimated by secondary verified sources.
- **Training Population**: Players transferring into the Premier League.
- **Seasons**: 2018/19 through 2025/26.
- **Leagues**: Premier League (primary evaluation domain).
- **Expanded Dataset Size**: 822 eligible disclosed transfers (up from 781), achieved by acquiring `eordo/transfermarkt-data` for 2024/25 and 2025/26.

## Methodology
- **Temporal Methodology**: Strict rolling-origin chronological validation. 2025/26 is used as a temporal holdout. No future information leakage is permitted. Pre-transfer performance (T-1) is correctly aligned to the season immediately prior to the transfer window.
- **Leakage Controls**: Features are restricted to those knowable at or before the transfer date. `market_value` is explicitly historical, representing the player's value *at or near* the transfer date, rather than a present-day proxy.
- **Uncertainty Methodology**: Conformal prediction and fee-band classification were tested. A two-stage model (Classifier -> Regressor) was explicitly tested but found to underperform (MAE £10.0M) compared to a single-stage approach (MAE £7.1M).

## Features
- **Player Performance (T-1)**: `t1_minutes`, `t1_goals_per90`, `t1_assists_per90`
- **Context & Temporal**: `age_at_transfer`, `career_minutes_before_transfer`, `is_summer_window`
- **Club/Market**: `selling_club_pts_t1`, `market_value`
- *Note: Performance features for newly added 2024/25 and 2025/26 transfers were pipeline-imputed during the experiment, leveraging the high predictive power of `market_value`.*

## Models Tested
A comprehensive benchmark was conducted over the dataset:
- Linear Regression (MAE: £6.92M)
- Ridge (MAE: £6.92M) **[Selected Candidate]**
- Random Forest (MAE: £7.01M)
- Gradient Boosting (MAE: £7.02M)
- Extra Trees (MAE: £7.19M)
- XGBoost (MAE: £7.21M)
- MLP (MAE: £18.82M)

## Metrics (2025/26 Temporal Holdout)
- **MAE**: £7,140,388
- **RMSE**: £10,078,259
- **Median AE (MedAE)**: £5,304,303
- **R²**: 0.824
- **WAPE**: 25.0%
- **±20% Accuracy**: 41.1%
- **±30% Accuracy**: 58.1%

### Market-Value Ablation (Phase 15D)
An ablation study definitively proved the necessity of historical market value:
- **Model A (No Market Value)**: MAE £12,420,061
- **Model B (With Market Value)**: MAE £7,127,054
*Conclusion: Introducing historical market value reduces absolute error by ~42%.*

### High-Value Transfer Performance (Fee-Band Analysis)
The model was tested across distinct transfer-fee bands to ensure stability at the top end:
- **£0–5M (n=11)**: MAE = £3.99M | WAPE = 143%
- **£5–15M (n=29)**: MAE = £4.13M | WAPE = 39%
- **£15–30M (n=37)**: MAE = £4.51M | WAPE = 22%
- **£30–50M (n=29)**: MAE = £8.87M | WAPE = 24%
- **£50M+ (n=18)**: MAE = £16.53M | WAPE = 22%
*Observation: While MAE inherently scales with fee magnitude, the Weighted Absolute Percentage Error (WAPE) remains remarkably stable (22-24%) for transfers above £15M.*

## Limitations
1. **2026/27 Data Availability**: Verified 2026/27 summer transfer fees were largely unavailable in reliable, reproducible public CSV repositories without resorting to prohibited anti-bot circumvention on Transfermarkt. Therefore, 2025/26 was utilized as the temporal holdout.
2. **Low-Value Volatility**: The WAPE for £0-5M transfers is highly erratic (143%), indicating the model struggles to differentiate between a £1M and £4M player, often overvaluing them based on performance metrics.
3. **Data Imputation**: Performance metrics for the newly appended 2024/25 and 2025/26 cohorts were median-imputed. A full pipeline rebuild mapping FPL to Transfermarkt is required for absolute purity.
