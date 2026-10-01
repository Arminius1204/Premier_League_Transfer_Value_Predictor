# Phase 16 Model Experiment Report

## 1. Objective
To benchmark baseline machine learning models on the new Phase 16 candidate dataset, ensuring the richer data foundation translates to improved predictive performance before diving into complex feature engineering or deploying V4. Note: `market_value` was explicitly excluded to ensure the model learns from fundamental performance and context data.

## 2. Experimental Setup
- **Dataset**: `transfer_features_fee_v4_candidate.csv` (781 transfers)
- **Target Variable**: `log_fee_gbp`
- **Features Used**: `age_at_transfer`, `t1_minutes`, `t1_goals_per90`, `t1_assists_per90`, `is_foreign_import`, `is_summer_window`, `career_minutes_before_transfer`, `career_goals_before_transfer`, `t1_selling_club_pts`, `t1_selling_club_gd`
- **Imputation**: Median imputation for missing values (imputation drastically reduced compared to Phase 15).
- **Validation**: 5-Fold Cross-Validation
- **Models Benchmarked**: Ridge Regression, Random Forest, XGBoost

## 3. Results Comparison

### Previous Baseline (Phase 15C - V4)
- **Random Forest R²**: 0.071
- **Random Forest MAE**: £13.65M
- **£50M+ Tier MAE**: £52.82M
- **Haaland Prediction**: £27.44M vs £51.54M actual

### Current Baseline (Phase 16 - Multi-League Data)
| Metric | Ridge Regression | Random Forest | XGBoost |
|---|---|---|---|
| R² | 0.111 | 0.204 | 0.191 |
| Overall MAE | £24.94M | £9.65M | £9.88M |
| £50M+ Tier MAE | £52.82M | £44.30M | £40.74M |
| Haaland Prediction | £114.46M | £35.31M | £42.13M |

## 4. Analysis
1. **Massive Error Reduction:** Random Forest MAE dropped from £13.65M to £9.65M, breaking the £10M barrier solely by improving data quality and coverage.
2. **High-Value Accuracy:** The £50M+ transfer error (a historically difficult segment) improved substantially. XGBoost achieved a £40.74M MAE on this tier, a >£12M improvement over the previous iteration.
3. **Haaland Reality Check:** Erling Haaland's predicted transfer fee jumped from £27.44M (in V4, where his stats were missing) to £42.13M (XGBoost) and £35.31M (Random Forest). This confirms that supplying the models with genuine Bundesliga performance data (22 goals in 1911 minutes) correctly influences the predictions upward toward his actual £51.54M fee.
4. **Conclusion:** Data quality was indeed the bottleneck. With the multi-league foundation firmly established, the models possess a much stronger signal. Future phases can now safely return to optimizing model architecture, introducing market value (if permitted/adjusted), and engineering more complex features.
