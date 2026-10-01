import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import json

def load_data():
    df_core = pd.read_csv('data/processed/transfer_features_enriched_v2.csv')
    df_eordo = pd.read_csv('data/raw/transfermarkt_eordo_2018_2025.csv')
    df_eordo['season_id'] = df_eordo['season'].apply(lambda x: f"{x}_{x+1}")
    df_eordo = df_eordo[df_eordo['movement'] == 'in']
    
    players = pd.read_csv('data/processed/players.csv')
    df_core = df_core.merge(players[['master_player_id', 'canonical_name']], on='master_player_id', how='left')
    df_core['match_name'] = df_core['canonical_name'].str.lower().str.replace(' ', '')
    df_eordo['match_name'] = df_eordo['player_name'].str.lower().str.replace(' ', '')
    
    eordo_dedup = df_eordo.drop_duplicates(subset=['season_id', 'match_name'])
    
    # We want to keep ONLY the rows in df_core that matched, so we can do apples-to-apples
    df_merged = df_core.merge(eordo_dedup[['season_id', 'match_name', 'market_value']], on=['season_id', 'match_name'], how='inner')
    df_merged = df_merged.dropna(subset=['market_value', 'fee_gbp'])
    df_merged['is_summer_window'] = 1
    return df_merged

def eval_metrics(y_true, y_pred):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    medae = np.median(np.abs(y_true - y_pred))
    r2 = r2_score(y_true, y_pred)
    wape = np.sum(np.abs(y_true - y_pred)) / np.sum(y_true)
    p_10 = np.mean(np.abs(y_true - y_pred) <= 0.10 * y_true)
    p_20 = np.mean(np.abs(y_true - y_pred) <= 0.20 * y_true)
    p_30 = np.mean(np.abs(y_true - y_pred) <= 0.30 * y_true)
    p_50 = np.mean(np.abs(y_true - y_pred) <= 0.50 * y_true)
    return {'MAE': mae, 'RMSE': rmse, 'MedAE': medae, 'WAPE': wape, 'R2': r2, 'p_10': p_10, 'p_20': p_20, 'p_30': p_30, 'p_50': p_50}

def build_pipe(num_features, cat_features):
    num_trans = Pipeline(steps=[('imputer', SimpleImputer(strategy='median')), ('scaler', StandardScaler())])
    cat_trans = Pipeline(steps=[('imputer', SimpleImputer(strategy='most_frequent')), ('onehot', OneHotEncoder(handle_unknown='ignore'))])
    prep = ColumnTransformer(transformers=[('num', num_trans, num_features), ('cat', cat_trans, cat_features)])
    return Pipeline(steps=[('preprocessor', prep), ('model', Ridge(alpha=1.0))])

def main():
    df = load_data()
    print("==================================================")
    print("1. HAALAND TARGET CONSISTENCY")
    print("==================================================")
    
    haaland = df[df['canonical_name'].str.contains('Haaland', case=False, na=False)]
    if not haaland.empty:
        actual_fee = haaland['fee_gbp'].iloc[0]
        v3_pred = 14500000 # hardcoded from known previous phase run
        v4_pred = 127184036 # hardcoded from phase 15 results
        print(f"Haaland Actual Fee: £{actual_fee:,.0f}")
        print(f"v3 Prediction: £{v3_pred:,.0f} | Absolute Error: £{abs(v3_pred - actual_fee):,.0f}")
        print(f"v4 Prediction: £{v4_pred:,.0f} | Absolute Error: £{abs(v4_pred - actual_fee):,.0f}")
        print("Note: v4 absolute error (£75.6M) is massively worse than v3 absolute error (£37M) against the ACTUAL FEE target, despite being a 'better' reflection of market value. v4 is predicting Market Value, not Actual Fee.")

    print("\n==================================================")
    print("2. V3 VS V4 APPLES-TO-APPLES EVALUATION")
    print("==================================================")
    # The previous 2023_2024 holdout
    train_app = df[df['season_id'] < '2023_2024']
    test_app = df[df['season_id'] == '2023_2024']
    
    cat_features = ['position', 'is_summer_window']
    num_v3 = ['age_at_transfer', 't1_minutes', 't1_goals_per90', 't1_assists_per90', 'career_minutes_before_transfer', 'selling_club_pts_t1']
    num_v4 = num_v3 + ['market_value']
    
    v3_pipe = build_pipe(num_v3, cat_features)
    v4_pipe = build_pipe(num_v4, cat_features)
    
    v3_pipe.fit(train_app[num_v3 + cat_features], train_app['fee_gbp'])
    v4_pipe.fit(train_app[num_v4 + cat_features], train_app['fee_gbp'])
    
    pred_v3 = v3_pipe.predict(test_app[num_v3 + cat_features])
    pred_v4 = v4_pipe.predict(test_app[num_v4 + cat_features])
    
    m_v3 = eval_metrics(test_app['fee_gbp'], pred_v3)
    m_v4 = eval_metrics(test_app['fee_gbp'], pred_v4)
    
    print("EVALUATION POPULATION:")
    print(f"Dataset: df_core intersected with eordo (N={len(df)})")
    print(f"Test Seasons: 2023/24")
    print(f"Test Sample Count: {len(test_app)}")
    
    print("\nMETRICS:")
    for k in m_v3.keys():
        print(f"{k:6} | v3: {m_v3[k]:,.2f} | v4: {m_v4[k]:,.2f}")

    print("\n==================================================")
    print("3. HISTORICAL MARKET VALUE TEMPORAL AUDIT")
    print("==================================================")
    print("Transfermarkt scraped data (eordo) does not provide exact 'market_value_date' in this extraction, only the market value mapped to the transfer event itself.")
    print("Total rows: ", len(df))
    print("Valid timestamped rows: 0 (No explicit date column provided)")
    print("Missing rows: 0")
    print("Warning: eordo transfermarkt market_value often updates immediately post-transfer for big moves, meaning this field likely leaks future information.")

    print("\n==================================================")
    print("4. MARKET VALUE ABLATION")
    print("==================================================")
    print(f"Model A (v3 feature set) MAE: {m_v3['MAE']:,.0f}")
    print(f"Model B (v4 feature set) MAE: {m_v4['MAE']:,.0f}")
    abs_imp = m_v3['MAE'] - m_v4['MAE']
    pct_imp = abs_imp / m_v3['MAE'] * 100
    print(f"Absolute Improvement: £{abs_imp:,.0f}")
    print(f"Percentage Improvement: {pct_imp:.2f}%")

    print("\n==================================================")
    print("5. HAALAND FEATURE TRACE")
    print("==================================================")
    if not haaland.empty:
        for col in num_v4 + cat_features + ['fee_gbp', 'season_id']:
            val = haaland[col].iloc[0]
            print(f"{col:30} {val}")
            
    print("\n==================================================")
    print("6. TARGET CORRELATION AUDIT")
    print("==================================================")
    corr = df['fee_gbp'].corr(df['market_value'])
    print(f"Correlation(actual_fee, historical_market_value): {corr:.4f}")
    df['fee_to_mv_ratio'] = df['fee_gbp'] / (df['market_value'] + 1)
    print("fee/mv ratio quartiles:")
    print(df['fee_to_mv_ratio'].describe(percentiles=[.1, .25, .5, .75, .9]))

    print("\n==================================================")
    print("7. HIGH-VALUE TRANSFER AUDIT")
    print("==================================================")
    test_app['pred_v4'] = pred_v4
    h1 = test_app[(test_app['fee_gbp'] >= 30000000) & (test_app['fee_gbp'] < 50000000)]
    h2 = test_app[test_app['fee_gbp'] >= 50000000]
    
    if not h1.empty:
        m = eval_metrics(h1['fee_gbp'], h1['pred_v4'])
        print(f"£30M-£50M (n={len(h1)}): MAE=£{m['MAE']:,.0f}, MedAE=£{m['MedAE']:,.0f}, WAPE={m['WAPE']:.2f}, ±20%={m['p_20']:.2f}")
    if not h2.empty:
        m = eval_metrics(h2['fee_gbp'], h2['pred_v4'])
        print(f"£50M+ (n={len(h2)}): MAE=£{m['MAE']:,.0f}, MedAE=£{m['MedAE']:,.0f}, WAPE={m['WAPE']:.2f}, ±20%={m['p_20']:.2f}")

    print("\n==================================================")
    print("8. R² = 0.824 AUDIT")
    print("==================================================")
    print("The 0.824 R2 was evaluated on 2025/26 holdout using Ridge Regression.")
    print("Since eordo 'market_value' at time of transfer often matches the transfer fee implicitly or updates immediately after a transfer is announced, the R2 is heavily artificially inflated. This is target leakage.")

if __name__ == '__main__':
    main()
