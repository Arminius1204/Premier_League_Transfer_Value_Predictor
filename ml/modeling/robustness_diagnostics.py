import pandas as pd
import numpy as np
from pathlib import Path
import json
import warnings
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import Ridge, Lasso, HuberRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

warnings.filterwarnings('ignore')

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "transfer_features_candidate.csv"
DOCS_DIR = PROJECT_ROOT / "docs"
OUT_DIR = PROJECT_ROOT / "data" / "processed"

FEATURE_SET_CORE = [
    'age_at_transfer', 'age_squared', 'position', 'nationality',
    'prev_season_points', 'prev_season_points_per_match', 'prev_season_gd'
]

def build_preprocessor(feature_list, df):
    num_cols = [c for c in feature_list if df[c].dtype in ['float64', 'int64'] and c not in ['position', 'nationality']]
    cat_cols = [c for c in feature_list if c not in num_cols]
    
    num_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    cat_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='UNKNOWN')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    return ColumnTransformer(transformers=[
        ('num', num_transformer, num_cols),
        ('cat', cat_transformer, cat_cols)
    ])

def run_diagnostics():
    df = pd.read_csv(DATA_PATH).dropna(subset=['fee_gbp'])
    df['transfer_date'] = pd.to_datetime(df['transfer_date'], errors='coerce')
    
    # 1. Temporal Split Audit
    seasons = df['season_id'].unique()
    audit_lines = ["# Temporal Split Audit\n"]
    for s in sorted(seasons):
        sdf = df[df['season_id'] == s]
        audit_lines.append(f"## Season {s}")
        audit_lines.append(f"- Count: {len(sdf)}")
        audit_lines.append(f"- Min Date: {sdf['transfer_date'].min().date() if not pd.isna(sdf['transfer_date'].min()) else 'Unknown'}")
        audit_lines.append(f"- Max Date: {sdf['transfer_date'].max().date() if not pd.isna(sdf['transfer_date'].max()) else 'Unknown'}")
        audit_lines.append(f"- Target Median (GBP): {sdf['fee_gbp'].median():,.2f}")
        audit_lines.append(f"- Target Mean (GBP): {sdf['fee_gbp'].mean():,.2f}")
        audit_lines.append(f"- Target Min (GBP): {sdf['fee_gbp'].min():,.2f}")
        audit_lines.append(f"- Target Max (GBP): {sdf['fee_gbp'].max():,.2f}\n")
        
    with open(DOCS_DIR / "phase8_temporal_distribution_audit.md", "w") as f:
        f.writelines([line + "\n" for line in audit_lines])

    train_df = df[df['season_id'].isin(['2021_2022', '2022_2023'])].copy()
    test_df = df[df['season_id'].isin(['2023_2024', '2023'])].copy()
    
    # 2. Target Distribution Shift
    train_fee = train_df['fee_gbp']
    test_fee = test_df['fee_gbp']
    
    # 3. Feature Distribution Shift
    shift_data = []
    for col in FEATURE_SET_CORE:
        if df[col].dtype in ['float64', 'int64']:
            tr_mean = train_df[col].mean()
            te_mean = test_df[col].mean()
            diff = te_mean - tr_mean
            shift_data.append({
                'feature': col,
                'train_stat': f"{tr_mean:.2f} (mean)",
                'test_stat': f"{te_mean:.2f} (mean)",
                'difference': f"{diff:.2f}",
                'shift_flag': 'High' if abs(diff/(tr_mean+1e-5)) > 0.2 else 'Normal',
                'interpretation': 'Check temporal drift'
            })
    pd.DataFrame(shift_data).to_csv(OUT_DIR / "feature_distribution_shift.csv", index=False)
    
    # 4. Fee Range Generalization (Quantiles from Train)
    q25, q50, q75 = train_fee.quantile([0.25, 0.50, 0.75])
    def get_band(fee):
        if fee <= q25: return 'LOW'
        elif fee <= q50: return 'MEDIUM'
        elif fee <= q75: return 'HIGH'
        else: return 'VERY_HIGH'
    
    train_df['fee_band'] = train_df['fee_gbp'].apply(get_band)
    test_df['fee_band'] = test_df['fee_gbp'].apply(get_band)

    # 9. Simple Model Benchmark
    preprocessor = build_preprocessor(FEATURE_SET_CORE, df)
    X_train = train_df[FEATURE_SET_CORE]
    y_train = train_df['fee_gbp']
    X_test = test_df[FEATURE_SET_CORE]
    y_test = test_df['fee_gbp']

    benchmarks = {
        'Ridge': Ridge(alpha=1.0),
        'Lasso': Lasso(alpha=1000.0),
        'HuberRegressor': HuberRegressor()
    }
    
    benchmark_results = []
    best_pipe = None
    for name, model in benchmarks.items():
        pipe = Pipeline(steps=[('preprocessor', preprocessor), ('model', model)])
        pipe.fit(X_train, y_train)
        preds = np.maximum(pipe.predict(X_test), 0)
        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)
        benchmark_results.append({'model': name, 'MAE': mae, 'R2': r2})
        if name == 'Ridge':
            best_pipe = pipe
            
    pd.DataFrame(benchmark_results).to_csv(OUT_DIR / "regularized_benchmarks.csv", index=False)
    
    # 6. Error Decomposition
    test_df['predicted_fee'] = np.maximum(best_pipe.predict(X_test), 0)
    test_df['absolute_error'] = np.abs(test_df['predicted_fee'] - test_df['fee_gbp'])
    test_df['signed_error'] = test_df['predicted_fee'] - test_df['fee_gbp']
    test_df.to_csv(OUT_DIR / "error_analysis.csv", index=False)
    
    # 18. Model Stability
    seeds = [42, 100, 2023, 999, 7]
    rf_maes = []
    for s in seeds:
        pipe = Pipeline(steps=[('preprocessor', preprocessor), ('model', RandomForestRegressor(n_estimators=50, max_depth=3, random_state=s))])
        pipe.fit(X_train, y_train)
        rf_maes.append(mean_absolute_error(y_test, pipe.predict(X_test)))
        
    stability_data = {'mean_mae': np.mean(rf_maes), 'std_mae': np.std(rf_maes)}
    with open(OUT_DIR / "model_stability.json", "w") as f:
        json.dump(stability_data, f)
        
    # 10. Walk-Forward Experiments
    # Exp A: Train 21/22, Val 22/23
    t1 = df[df['season_id'] == '2021_2022']
    v1 = df[df['season_id'] == '2022_2023']
    if len(t1) > 0 and len(v1) > 0:
        pipe = Pipeline(steps=[('preprocessor', preprocessor), ('model', Ridge())])
        pipe.fit(t1[FEATURE_SET_CORE], t1['fee_gbp'])
        expA_mae = mean_absolute_error(v1['fee_gbp'], np.maximum(pipe.predict(v1[FEATURE_SET_CORE]), 0))
    else:
        expA_mae = None
        
    walk_data = {'ExpA_Train_2122_Val_2223_MAE': expA_mae}
    with open(OUT_DIR / "walk_forward.json", "w") as f:
        json.dump(walk_data, f)

if __name__ == "__main__":
    run_diagnostics()
