import pandas as pd
import numpy as np
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, r2_score
import sys
import warnings
warnings.filterwarnings('ignore')

def run_experiment():
    df = pd.read_csv('data/processed/transfer_features_fee_v4_candidate.csv')
    
    # Drop rows without target
    df = df.dropna(subset=['log_fee_gbp'])
    
    features = [
        'age_at_transfer', 't1_minutes', 't1_goals_per90', 't1_assists_per90',
        'is_foreign_import', 'is_summer_window', 'career_minutes_before_transfer',
        'career_goals_before_transfer', 't1_selling_club_pts', 't1_selling_club_gd'
    ]
    
    X = df[features].copy()
    y = df['log_fee_gbp']
    fee_gbp = df['fee_gbp']
    
    models = {
        'Ridge Regression': Ridge(alpha=1.0),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
        'XGBoost': xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42, objective='reg:squarederror')
    }
    
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    
    results = []
    
    for name, model in models.items():
        pipe = Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler()),
            ('model', model)
        ])
        
        preds = np.zeros(len(df))
        
        for train_idx, test_idx in kf.split(X):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
            
            pipe.fit(X_train, y_train)
            preds[test_idx] = pipe.predict(X_test)
            
        r2 = r2_score(y, preds)
        
        # Calculate actual fee metrics
        actual_fees = fee_gbp
        pred_fees = np.exp(preds)
        
        mae = mean_absolute_error(actual_fees, pred_fees) / 1e6
        
        # high value mae
        high_mask = actual_fees >= 50e6
        high_mae = mean_absolute_error(actual_fees[high_mask], pred_fees[high_mask]) / 1e6 if high_mask.sum() > 0 else np.nan
        
        # Haaland prediction
        haaland_idx = df.index[df['canonical_name'] == 'erling haaland'].tolist()
        haaland_pred = pred_fees[haaland_idx[0]] / 1e6 if len(haaland_idx) > 0 else np.nan
        haaland_actual = actual_fees.iloc[haaland_idx[0]] / 1e6 if len(haaland_idx) > 0 else np.nan
        
        print(f"--- {name} ---")
        print(f"R²: {r2:.3f}")
        print(f"MAE: £{mae:.2f}M")
        print(f"£50M+ MAE: £{high_mae:.2f}M")
        if not np.isnan(haaland_pred):
            print(f"Haaland Pred: £{haaland_pred:.2f}M vs Actual £{haaland_actual:.2f}M")
        print()

if __name__ == "__main__":
    run_experiment()
