# Phase 11 Modeling Data Audit

## Core Dataset
- Rows: 781
- Columns: 16
- Numeric features: 11
- Categorical features: 5
- Duplicate transfer IDs: 0

### Missingness (%)
- age_at_transfer: 100.0%
- age_squared: 100.0%
- selling_club_pts_t1: 100.0%
- selling_club_gd_t1: 100.0%

### Constant Columns
- ['age_at_transfer', 'age_squared', 'position', 'selling_club_pts_t1', 'selling_club_gd_t1', 'transfer_month', 'is_summer_window']

## Enriched Dataset
- Rows: 781
- Columns: 28
- Numeric features: 23
- Categorical features: 5
- Duplicate transfer IDs: 0

### Missingness (%)
- age_at_transfer: 100.0%
- age_squared: 100.0%
- selling_club_pts_t1: 100.0%
- selling_club_gd_t1: 100.0%
- t1_minutes: 99.1%
- t1_goals: 99.1%
- t1_assists: 99.1%
- t1_bps: 99.1%
- t1_goals_per90: 99.2%
- t1_assists_per90: 99.2%
- t1_bps_per90: 99.2%
- t1_low_minutes_flag: 99.1%
- two_season_avg_minutes: 100.0%
- two_season_avg_goals: 100.0%
- goals_trend: 100.0%

### Constant Columns
- ['age_at_transfer', 'age_squared', 'position', 'selling_club_pts_t1', 'selling_club_gd_t1', 'transfer_month', 'is_summer_window', 'two_season_avg_minutes', 'two_season_avg_goals', 'goals_trend']

## Season Breakdown
season_id
2018_2019    136
2019_2020    124
2020_2021    100
2021_2022    112
2022_2023    158
2023_2024    151
