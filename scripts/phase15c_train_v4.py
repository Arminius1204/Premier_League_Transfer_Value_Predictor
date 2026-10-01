import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import json
import os

def main():
    # Load enriched features
    df = pd.read_csv("data/processed/transfer_features_enriched_v2.csv")
    
    # 1. Rebuild candidate dataset (Leakage-free)
    # Define reliable features based on missingness audit
    numeric_features = [
        "previous_transfer_count",
        "career_minutes_before_transfer",
        "career_goals_before_transfer",
        "t1_minutes",
        "t1_goals",
        "t1_assists"
    ]
    
    categorical_features = [
        "position",
        "is_summer_window"
    ]
    
    # Drop rows without a valid target
    df = df.dropna(subset=["log_fee_gbp", "fee_gbp"])
    
    # Create missingness indicator
    df["is_foreign_import"] = df["t1_minutes"].isnull().astype(int)
    numeric_features.append("is_foreign_import")
    
    # Save candidate dataset
    columns_to_keep = ["transfer_id", "master_player_id", "season_id", "player_name", "transfer_date", "fee_gbp", "log_fee_gbp"] + numeric_features + categorical_features
    # wait, player_name is not in transfer_features_enriched_v2.csv. It has master_player_id
    # I need to join with master_player.csv to get canonical_name
    master = pd.read_csv("data/entity_resolution/master_player.csv")
    df = df.merge(master[["master_player_id", "canonical_name"]], on="master_player_id", how="left")
    df.rename(columns={"canonical_name": "player_name"}, inplace=True)
    
    columns_to_keep = ["transfer_id", "master_player_id", "season_id", "player_name", "transfer_date", "fee_gbp", "log_fee_gbp"] + numeric_features + categorical_features
    df_candidate = df[columns_to_keep].copy()
    
    df_candidate.to_csv("data/processed/transfer_features_fee_v4_candidate.csv", index=False)
    print("Saved transfer_features_fee_v4_candidate.csv")
    
    # 2. Train leakage-free model (RF)
    X = df_candidate[numeric_features + categorical_features]
    y = df_candidate["log_fee_gbp"]
    
    # Preprocessor
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])
        
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42))
    ])
    
    # Chronological Split
    df_candidate = df_candidate.sort_values(by="transfer_date")
    split_idx = int(len(df_candidate) * 0.8)
    
    X_train = df_candidate[numeric_features + categorical_features].iloc[:split_idx]
    y_train = df_candidate["log_fee_gbp"].iloc[:split_idx]
    
    X_test = df_candidate[numeric_features + categorical_features].iloc[split_idx:]
    y_test = df_candidate["log_fee_gbp"].iloc[split_idx:]
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred_log = model.predict(X_test)
    y_pred = np.exp(y_pred_log)
    y_true = np.exp(y_test)
    
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_test, y_pred_log)
    
    print(f"Leakage-Free RF Model (V4) MAE: £{mae:,.2f}")
    print(f"Leakage-Free RF Model (V4) R2: {r2:.4f}")
    
    # 3. High-Value and Haaland Tests
    haaland = df_candidate[df_candidate["player_name"] == "erling haaland"]
    if not haaland.empty:
        haaland_pred_log = model.predict(haaland[numeric_features + categorical_features])
        haaland_pred = np.exp(haaland_pred_log[0])
        print(f"\nHaaland V4 Prediction: £{haaland_pred:,.2f}")
        print(f"Haaland Actual Fee: £{haaland['fee_gbp'].iloc[0]:,.2f}")
        print(f"Haaland Absolute Error: £{abs(haaland_pred - haaland['fee_gbp'].iloc[0]):,.2f}")
    else:
        print("Haaland not found in candidate dataset.")
        
    high_value = df_candidate[df_candidate["fee_gbp"] > 50000000]
    hv_preds_log = model.predict(high_value[numeric_features + categorical_features])
    hv_preds = np.exp(hv_preds_log)
    hv_mae = mean_absolute_error(high_value["fee_gbp"], hv_preds)
    print(f"\nHigh Value Transfer MAE (>£50m): £{hv_mae:,.2f}")
    
    # Save Model
    os.makedirs("models/v4", exist_ok=True)
    joblib.dump(model, "models/v4/leakage_free_rf.joblib")
    print("\nSaved V4 Model to models/v4/leakage_free_rf.joblib")
    
if __name__ == "__main__":
    main()
