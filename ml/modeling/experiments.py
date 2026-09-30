import os
import json
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.dummy import DummyRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score, median_absolute_error

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "transfer_features_candidate.csv"
RESULTS_PATH = PROJECT_ROOT / "data" / "processed" / "model_experiment_results.csv"
MODELS_DIR = PROJECT_ROOT / "models"
CONFIG_PATH = PROJECT_ROOT / "configs" / "model_configs.json"

FEATURE_SET_CORE = [
    'age_at_transfer', 'age_squared', 'position', 'nationality',
    'prev_season_points', 'prev_season_points_per_match', 'prev_season_gd'
]

FEATURE_SET_ENRICHED = FEATURE_SET_CORE + [
    'prev_season_minutes', 'low_minutes_flag', 'prev_season_goals_per90', 'prev_season_xg_per90'
]

def wape(y_true, y_pred):
    return np.sum(np.abs(y_true - y_pred)) / np.sum(np.abs(y_true))

def run_experiments():
    df = pd.read_csv(DATA_PATH)
    
    # We drop any records that inexplicably have missing targets
    df = df.dropna(subset=['fee_gbp', 'log_fee_gbp'])
    
    # Split: Train (2021/22, 2022/23) vs Test (2023/24)
    # Using '2023_2024' and '2023' (which both map to Summer 23/24).
    test_seasons = ['2023_2024', '2023']
    train_df = df[~df['season_id'].isin(test_seasons)].copy()
    test_df = df[df['season_id'].isin(test_seasons)].copy()
    
    # We will define a list of models
    models = {
        'Baseline_Median': DummyRegressor(strategy='median'),
        'Baseline_Mean': DummyRegressor(strategy='mean'),
        'LinearRegression': LinearRegression(),
        'RandomForest': RandomForestRegressor(n_estimators=100, max_depth=5, min_samples_leaf=4, random_state=42),
        'GradientBoosting': GradientBoostingRegressor(n_estimators=100, max_depth=3, learning_rate=0.05, random_state=42),
        'XGBoost': XGBRegressor(n_estimators=100, max_depth=3, learning_rate=0.05, random_state=42),
        'MLPRegressor': MLPRegressor(hidden_layer_sizes=(32, 16), early_stopping=True, max_iter=1000, random_state=42)
    }
    
    # Save configs
    configs = {
        name: str(model.get_params()) for name, model in models.items()
    }
    with open(CONFIG_PATH, 'w') as f:
        json.dump(configs, f, indent=4)
        
    results = []
    
    for fs_name, feature_list in [('CORE', FEATURE_SET_CORE), ('ENRICHED', FEATURE_SET_ENRICHED)]:
        # Define Preprocessor
        num_cols = [c for c in feature_list if df[c].dtype in ['float64', 'int64'] and c not in ['position', 'nationality', 'low_minutes_flag']]
        cat_cols = [c for c in feature_list if c not in num_cols]
        
        num_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler()) # Standardizing helps MLP & LinearReg
        ])
        cat_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='UNKNOWN')),
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ])
        
        preprocessor = ColumnTransformer(transformers=[
            ('num', num_transformer, num_cols),
            ('cat', cat_transformer, cat_cols)
        ])
        
        for target_type in ['raw', 'log']:
            target_col = 'fee_gbp' if target_type == 'raw' else 'log_fee_gbp'
            
            y_train = train_df[target_col].values
            y_test = test_df[target_col].values
            
            for model_name, model in models.items():
                # Avoid running complex models on ENRICHED if data is extremely sparse?
                # Actually, sklearn pipelines handle missing data gracefully.
                pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('model', model)])
                
                pipeline.fit(train_df, y_train)
                preds = pipeline.predict(test_df)
                
                # Transform back to GBP if log
                if target_type == 'log':
                    preds_gbp = np.expm1(preds)
                else:
                    preds_gbp = preds
                    
                # Fix negative predictions for raw target models (e.g. Linear Reg)
                preds_gbp = np.maximum(preds_gbp, 0)
                
                actual_gbp = test_df['fee_gbp'].values
                
                mae = mean_absolute_error(actual_gbp, preds_gbp)
                rmse = root_mean_squared_error(actual_gbp, preds_gbp)
                r2 = r2_score(actual_gbp, preds_gbp)
                med_ae = median_absolute_error(actual_gbp, preds_gbp)
                wape_val = wape(actual_gbp, preds_gbp)
                
                res = {
                    'experiment_id': f"{model_name}_{fs_name}_{target_type}",
                    'model': model_name,
                    'target_type': target_type,
                    'feature_set': fs_name,
                    'train_seasons': '2021_2022+2022_2023',
                    'test_season': '2023_2024',
                    'train_rows': len(train_df),
                    'test_rows': len(test_df),
                    'MAE': round(mae, 2),
                    'RMSE': round(rmse, 2),
                    'R2': round(r2, 4),
                    'median_absolute_error': round(med_ae, 2),
                    'WAPE': round(wape_val, 4)
                }
                results.append(res)
                
                # Save model artifact
                save_dir = MODELS_DIR / model_name.lower()
                save_dir.mkdir(parents=True, exist_ok=True)
                joblib.dump(pipeline, save_dir / f"{model_name}_{fs_name}_{target_type}.pkl")
                
    res_df = pd.DataFrame(results)
    res_df.to_csv(RESULTS_PATH, index=False)
    print("Experiments completed. Results saved to:", RESULTS_PATH)

if __name__ == "__main__":
    run_experiments()
