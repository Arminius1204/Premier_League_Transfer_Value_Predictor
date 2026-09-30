import pandas as pd
import numpy as np
from pathlib import Path
import joblib

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, median_absolute_error

from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

import warnings
warnings.filterwarnings("ignore")

DATA_DIR = Path("data/processed")
MODELS_DIR = Path("models/v3")
for p in ["selected_models", "ensemble", "preprocessors", "uncertainty", "explainability"]:
    (MODELS_DIR / p).mkdir(parents=True, exist_ok=True)

def wape(y_true, y_pred):
    return np.sum(np.abs(y_true - y_pred)) / np.sum(y_true)

def build_preprocessor(numeric_features, categorical_features):
    num_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    cat_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='UNKNOWN')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    return ColumnTransformer(transformers=[
        ('num', num_transformer, numeric_features),
        ('cat', cat_transformer, categorical_features)
    ])

def run_ensembling():
    df = pd.read_csv(DATA_DIR / "transfer_features_enriched_v2.csv")
    seasons = ["2018_2019", "2019_2020", "2020_2021", "2021_2022", "2022_2023", "2023_2024"]
    
    meta_cols = ["transfer_id", "master_player_id", "season_id", "transfer_date", "fee_gbp", "log_fee_gbp"]
    features = [c for c in df.columns if c not in meta_cols]
    num_features = df[features].select_dtypes(include=np.number).columns.tolist()
    cat_features = df[features].select_dtypes(exclude=np.number).columns.tolist()
    
    models_config = {
        "Ridge": Ridge(alpha=10.0),
        "XGBoost": XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, random_state=42),
        "RandomForest": RandomForestRegressor(n_estimators=100, max_depth=10, min_samples_leaf=4, random_state=42)
    }
    
    experiments = [
        {"id": 1, "train": seasons[:1], "val": seasons[1]},
        {"id": 2, "train": seasons[:2], "val": seasons[2]},
        {"id": 3, "train": seasons[:3], "val": seasons[3]},
        {"id": 4, "train": seasons[:4], "val": seasons[4]},
        {"id": 5, "train": seasons[:5], "val": seasons[5]}  # Final Holdout
    ]
    
    oof_records = []
    
    # 1. Historical Validation (Folds 1-4)
    for exp in experiments[:-1]:
        train_mask = df["season_id"].isin(exp["train"])
        val_mask = df["season_id"] == exp["val"]
        
        X_train = df[train_mask]
        X_val = df[val_mask]
        
        y_train = X_train["fee_gbp"].values
        y_val = X_val["fee_gbp"].values
        
        preprocessor = build_preprocessor(num_features, cat_features)
        X_train_proc = preprocessor.fit_transform(X_train[features])
        X_val_proc = preprocessor.transform(X_val[features])
        
        fold_preds = {"transfer_id": X_val["transfer_id"].values, "season_id": X_val["season_id"].values, "actual_fee": y_val}
        
        for name, model in models_config.items():
            model.fit(X_train_proc, y_train)
            pred = np.maximum(model.predict(X_val_proc), 0)
            fold_preds[name] = pred
            
            for i, tid in enumerate(X_val["transfer_id"].values):
                oof_records.append({
                    "transfer_id": tid,
                    "season": exp["val"],
                    "actual_fee": y_val[i],
                    "model": name,
                    "prediction": pred[i],
                    "fold": exp["id"],
                    "feature_set": "Enriched"
                })

    oof_df = pd.DataFrame(oof_records)
    oof_df.to_csv(DATA_DIR / "oof_predictions_v3.csv", index=False)
    
    # 2. Compute Ensemble Weights using Historical OOF
    model_maes = oof_df.groupby("model").apply(lambda x: mean_absolute_error(x["actual_fee"], x["prediction"]))
    # Inverse MAE weighting
    inv_mae = 1.0 / model_maes
    weights = (inv_mae / inv_mae.sum()).to_dict()
    
    # 3. Compute Conformal Prediction Intervals using Historical OOF
    # We will use the Weighted Ensemble prediction as our center
    oof_pivoted = oof_df.pivot(index=["transfer_id", "actual_fee", "season", "fold"], columns="model", values="prediction").reset_index()
    
    weighted_oof_preds = np.zeros(len(oof_pivoted))
    for m in models_config.keys():
        weighted_oof_preds += oof_pivoted[m] * weights[m]
        
    abs_residuals = np.abs(oof_pivoted["actual_fee"] - weighted_oof_preds)
    q_80 = np.quantile(abs_residuals, 0.80)
    q_90 = np.quantile(abs_residuals, 0.90)
    
    # 4. Final Evaluation (Holdout)
    exp5 = experiments[-1]
    train_mask = df["season_id"].isin(exp5["train"])
    val_mask = df["season_id"] == exp5["val"]
    
    X_train = df[train_mask]
    X_val = df[val_mask]
    y_train = X_train["fee_gbp"].values
    y_val = X_val["fee_gbp"].values
    
    preprocessor = build_preprocessor(num_features, cat_features)
    X_train_proc = preprocessor.fit_transform(X_train[features])
    X_val_proc = preprocessor.transform(X_val[features])
    
    holdout_results = []
    val_preds = {}
    
    for name, model in models_config.items():
        model.fit(X_train_proc, y_train)
        pred = np.maximum(model.predict(X_val_proc), 0)
        val_preds[name] = pred
        
        # Save individuals
        joblib.dump(model, MODELS_DIR / f"selected_models/{name}_final.joblib")
        
        mae = mean_absolute_error(y_val, pred)
        r2 = r2_score(y_val, pred)
        holdout_results.append({"Model": name, "MAE": mae, "RMSE": np.sqrt(mean_squared_error(y_val, pred)), "R2": r2, "MedAE": median_absolute_error(y_val, pred), "WAPE": wape(y_val, pred)})
        
    joblib.dump(preprocessor, MODELS_DIR / "preprocessors/final_preprocessor.joblib")
    
    # Mean Ensemble
    mean_pred = np.mean([val_preds[m] for m in models_config.keys()], axis=0)
    holdout_results.append({"Model": "Mean_Ensemble", "MAE": mean_absolute_error(y_val, mean_pred), "RMSE": np.sqrt(mean_squared_error(y_val, mean_pred)), "R2": r2_score(y_val, mean_pred), "MedAE": median_absolute_error(y_val, mean_pred), "WAPE": wape(y_val, mean_pred)})
    
    # Median Ensemble
    median_pred = np.median([val_preds[m] for m in models_config.keys()], axis=0)
    holdout_results.append({"Model": "Median_Ensemble", "MAE": mean_absolute_error(y_val, median_pred), "RMSE": np.sqrt(mean_squared_error(y_val, median_pred)), "R2": r2_score(y_val, median_pred), "MedAE": median_absolute_error(y_val, median_pred), "WAPE": wape(y_val, median_pred)})
    
    # Weighted Ensemble
    weighted_pred = np.zeros(len(y_val))
    for m in models_config.keys():
        weighted_pred += val_preds[m] * weights[m]
    holdout_results.append({"Model": "Weighted_Ensemble", "MAE": mean_absolute_error(y_val, weighted_pred), "RMSE": np.sqrt(mean_squared_error(y_val, weighted_pred)), "R2": r2_score(y_val, weighted_pred), "MedAE": median_absolute_error(y_val, weighted_pred), "WAPE": wape(y_val, weighted_pred)})
    
    # Save Ensemble & Uncertainty metadata
    joblib.dump({
        "weights": weights,
        "q_80": q_80,
        "q_90": q_90,
        "features": features
    }, MODELS_DIR / "ensemble/ensemble_metadata.joblib")
    
    final_df = pd.DataFrame(holdout_results)
    final_df.to_csv(DATA_DIR / "ensemble_results_v3.csv", index=False)
    
    # Generate final holdout predictions w/ intervals
    holdout_preds = X_val[["transfer_id", "master_player_id", "season_id", "fee_gbp"]].copy()
    holdout_preds["predicted_fee"] = weighted_pred
    holdout_preds["lower_bound_80"] = np.maximum(weighted_pred - q_80, 0)
    holdout_preds["upper_bound_80"] = weighted_pred + q_80
    holdout_preds["lower_bound_90"] = np.maximum(weighted_pred - q_90, 0)
    holdout_preds["upper_bound_90"] = weighted_pred + q_90
    
    # Conformal Coverage Audit
    holdout_preds["covered_80"] = (holdout_preds["fee_gbp"] >= holdout_preds["lower_bound_80"]) & (holdout_preds["fee_gbp"] <= holdout_preds["upper_bound_80"])
    holdout_preds["covered_90"] = (holdout_preds["fee_gbp"] >= holdout_preds["lower_bound_90"]) & (holdout_preds["fee_gbp"] <= holdout_preds["upper_bound_90"])
    
    holdout_preds.to_csv(DATA_DIR / "final_holdout_predictions_v3.csv", index=False)
    
    print("OOF Weights:", weights)
    print(f"Historical 80% Margin: +-{q_80/1e6:.2f}M")
    print(f"Historical 90% Margin: +-{q_90/1e6:.2f}M")
    print("\nFinal Holdout Performance:")
    print(final_df.sort_values("MAE"))

if __name__ == "__main__":
    run_ensembling()
