import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, FunctionTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import json
import warnings
warnings.filterwarnings('ignore')

def load_data():
    df_core = pd.read_csv('data/processed/transfer_features_enriched_v2.csv')
    df_eordo = pd.read_csv('data/raw/transfermarkt_eordo_2018_2025.csv')
    
    # Preprocess eordo for merge
    df_eordo['season_id'] = df_eordo['season'].apply(lambda x: f"{x}_{x+1}")
    df_eordo = df_eordo[df_eordo['movement'] == 'in']
    
    players = pd.read_csv('data/processed/players.csv')
    df_core = df_core.merge(players[['master_player_id', 'canonical_name']], on='master_player_id', how='left')
    
    # Simplified merge
    df_core['match_name'] = df_core['canonical_name'].str.lower().str.replace(' ', '')
    df_eordo['match_name'] = df_eordo['player_name'].str.lower().str.replace(' ', '')
    
    # deduplicate eordo
    df_eordo = df_eordo.drop_duplicates(subset=['season_id', 'match_name'])
    
    merged = df_core.merge(df_eordo[['season_id', 'match_name', 'market_value']], 
                           on=['season_id', 'match_name'], 
                           how='left')
                           
    print(f"Matched {merged['market_value'].notna().sum()} out of {len(merged)} with market value.")
    return merged

def wape(y_true, y_pred):
    return np.sum(np.abs(y_true - y_pred)) / np.sum(y_true)

def eval_metrics(y_true, y_pred):
    return {
        "MAE": mean_absolute_error(y_true, y_pred),
        "RMSE": np.sqrt(mean_squared_error(y_true, y_pred)),
        "MedAE": np.median(np.abs(y_true - y_pred)),
        "R2": r2_score(y_true, y_pred),
        "WAPE": wape(y_true, y_pred),
        "p_10": np.mean(np.abs(y_true - y_pred) <= 0.10 * y_true),
        "p_20": np.mean(np.abs(y_true - y_pred) <= 0.20 * y_true),
        "p_30": np.mean(np.abs(y_true - y_pred) <= 0.30 * y_true),
        "p_50": np.mean(np.abs(y_true - y_pred) <= 0.50 * y_true)
    }

def build_pipeline(model, num_features, cat_features):
    num_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    cat_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    preprocessor = ColumnTransformer(transformers=[
        ('num', num_transformer, num_features),
        ('cat', cat_transformer, cat_features)
    ])
    return Pipeline(steps=[('preprocessor', preprocessor), ('model', model)])

def run_ablation(df):
    print("\n--- PHASE 15D: ABLATION ---")
    df = df.sort_values('season_id')
    
    num_features_A = ['age_at_transfer', 't1_minutes', 't1_goals_per90', 't1_assists_per90', 'career_minutes_before_transfer', 'selling_club_pts_t1']
    cat_features_A = ['position', 'is_summer_window']
    
    num_features_B = num_features_A + ['market_value']
    
    tscv = TimeSeriesSplit(n_splits=3)
    
    res_A, res_B = [], []
    
    df_eval = df.dropna(subset=['market_value']).copy()
    
    for train_idx, test_idx in tscv.split(df_eval):
        train, test = df_eval.iloc[train_idx], df_eval.iloc[test_idx]
        y_train, y_test = train['fee_gbp'], test['fee_gbp']
        
        pipe_A = build_pipeline(XGBRegressor(random_state=42), num_features_A, cat_features_A)
        pipe_A.fit(train[num_features_A + cat_features_A], y_train)
        preds_A = pipe_A.predict(test[num_features_A + cat_features_A])
        res_A.append(mean_absolute_error(y_test, preds_A))
        
        pipe_B = build_pipeline(XGBRegressor(random_state=42), num_features_B, cat_features_A)
        pipe_B.fit(train[num_features_B + cat_features_A], y_train)
        preds_B = pipe_B.predict(test[num_features_B + cat_features_A])
        res_B.append(mean_absolute_error(y_test, preds_B))
        
    print(f"Model A (No MV) MAE: {np.mean(res_A):,.0f}")
    print(f"Model B (With MV) MAE: {np.mean(res_B):,.0f}")
    
    return num_features_B, cat_features_A

def run_benchmarks(df, num_features, cat_features):
    print("\n--- PHASE 15F: MODEL BENCHMARK ---")
    df = df.dropna(subset=['market_value']).sort_values('season_id')
    features = num_features + cat_features
    
    models = {
        'Linear Regression': LinearRegression(),
        'Ridge': Ridge(alpha=1.0),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
        'Extra Trees': ExtraTreesRegressor(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingRegressor(random_state=42),
        'XGBoost': XGBRegressor(random_state=42),
        'MLP': MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42)
    }
    
    tscv = TimeSeriesSplit(n_splits=3)
    
    results = {}
    for name, model in models.items():
        maes = []
        for train_idx, test_idx in tscv.split(df):
            train, test = df.iloc[train_idx], df.iloc[test_idx]
            y_train, y_test = train['fee_gbp'], test['fee_gbp']
            
            pipe = build_pipeline(model, num_features, cat_features)
            pipe.fit(train[features], y_train)
            preds = pipe.predict(test[features])
            maes.append(mean_absolute_error(y_test, preds))
        results[name] = np.mean(maes)
        print(f"{name} MAE: {results[name]:,.0f}")
        
    best_model = min(results, key=results.get)
    print(f"\nBest Model: {best_model}")
    return models[best_model], results

def haaland_diagnostic(df, best_pipe, num_features, cat_features):
    print("\n--- PHASE 15K: HAALAND DIAGNOSTIC ---")
    haaland = df[df['canonical_name'].str.contains('Haaland', case=False, na=False)]
    if not haaland.empty:
        h_row = haaland.iloc[0:1]
        pred = best_pipe.predict(h_row[num_features + cat_features])[0]
        actual = h_row['fee_gbp'].values[0]
        mv = h_row['market_value'].values[0]
        print(f"Haaland Actual Transfer Fee: {actual:,.0f}")
        print(f"Haaland Historical Market Value: {mv:,.0f}")
        print(f"Haaland Predicted Fee (New Model): {pred:,.0f}")
    else:
        print("Haaland not found in dataset.")

if __name__ == '__main__':
    df = load_data()
    num_f, cat_f = run_ablation(df)
    best_mod, b_res = run_benchmarks(df, num_f, cat_f)
    
    df_clean = df.dropna(subset=['market_value'])
    final_pipe = build_pipeline(best_mod, num_f, cat_f)
    final_pipe.fit(df_clean[num_f + cat_f], df_clean['fee_gbp'])
    
    haaland_diagnostic(df_clean, final_pipe, num_f, cat_f)
    
    print("\nScript completed successfully.")
