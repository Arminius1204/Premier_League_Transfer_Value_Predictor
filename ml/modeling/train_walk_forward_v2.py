import pandas as pd
import numpy as np
from pathlib import Path
import json
import joblib

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, median_absolute_error

from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.base import BaseEstimator, RegressorMixin

import warnings
warnings.filterwarnings("ignore")

DATA_DIR = Path("data/processed")
MODELS_DIR = Path("models/v2")
for p in ["baseline", "linear", "ridge", "random_forest", "gradient_boosting", "xgboost", "mlp"]:
    (MODELS_DIR / p).mkdir(parents=True, exist_ok=True)

def wape(y_true, y_pred):
    return np.sum(np.abs(y_true - y_pred)) / np.sum(y_true)

class MeanBaseline(BaseEstimator, RegressorMixin):
    def fit(self, X, y):
        self.mean_ = np.mean(y)
        return self
    def predict(self, X):
        return np.full(shape=X.shape[0], fill_value=self.mean_)

class MedianBaseline(BaseEstimator, RegressorMixin):
    def fit(self, X, y):
        self.median_ = np.median(y)
        return self
    def predict(self, X):
        return np.full(shape=X.shape[0], fill_value=self.median_)

class PositionMedianBaseline(BaseEstimator, RegressorMixin):
    def fit(self, X, y):
        # Assumes X is a DataFrame and has 'position'
        df = X.copy()
        df['target'] = y
        self.pos_medians = df.groupby('position')['target'].median().to_dict()
        self.global_median = np.median(y)
        return self
    def predict(self, X):
        return np.array([self.pos_medians.get(p, self.global_median) for p in X['position']])

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

def run_experiments():
    core = pd.read_csv(DATA_DIR / "transfer_features_core_v2.csv")
    enriched = pd.read_csv(DATA_DIR / "transfer_features_enriched_v2.csv")
    
    seasons = ["2018_2019", "2019_2020", "2020_2021", "2021_2022", "2022_2023", "2023_2024"]
    
    experiments = [
        {"id": 1, "train": seasons[:1], "val": seasons[1]},
        {"id": 2, "train": seasons[:2], "val": seasons[2]},
        {"id": 3, "train": seasons[:3], "val": seasons[3]},
        {"id": 4, "train": seasons[:4], "val": seasons[4]},
        {"id": 5, "train": seasons[:5], "val": seasons[5]} # 5 is the final holdout
    ]
    
    models = {
        "Mean_Baseline": MeanBaseline(),
        "Median_Baseline": MedianBaseline(),
        "Pos_Median_Baseline": PositionMedianBaseline(),
        "Linear": LinearRegression(),
        "Ridge": Ridge(alpha=10.0),
        "RandomForest": RandomForestRegressor(n_estimators=100, max_depth=10, min_samples_leaf=4, random_state=42),
        "GradientBoosting": GradientBoostingRegressor(n_estimators=100, max_depth=5, learning_rate=0.05, random_state=42),
        "XGBoost": XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8, random_state=42),
        "MLP": MLPRegressor(hidden_layer_sizes=(64, 32), max_iter=500, early_stopping=True, random_state=42)
    }
    
    results = []
    
    for ds_name, df in [("Core", core), ("Enriched", enriched)]:
        meta_cols = ["transfer_id", "master_player_id", "season_id", "transfer_date", "fee_gbp", "log_fee_gbp"]
        features = [c for c in df.columns if c not in meta_cols]
        num_features = df[features].select_dtypes(include=np.number).columns.tolist()
        cat_features = df[features].select_dtypes(exclude=np.number).columns.tolist()
        
        for exp in experiments:
            train_mask = df["season_id"].isin(exp["train"])
            val_mask = df["season_id"] == exp["val"]
            
            X_train_raw = df[train_mask]
            X_val_raw = df[val_mask]
            
            if len(X_train_raw) == 0 or len(X_val_raw) == 0:
                continue
                
            for target_type in ["fee_gbp", "log_fee_gbp"]:
                y_train = X_train_raw[target_type].values
                # We always evaluate against raw fee for business metrics!
                y_val_actual_gbp = X_val_raw["fee_gbp"].values 
                
                # Preprocessor fitting
                preprocessor = build_preprocessor(num_features, cat_features)
                X_train_proc = preprocessor.fit_transform(X_train_raw[features])
                X_val_proc = preprocessor.transform(X_val_raw[features])
                
                for model_name, model in models.items():
                    # Fit
                    if "Baseline" in model_name:
                        # Baselines just use raw dataframe or raw y
                        model.fit(X_train_raw, y_train)
                        pred = model.predict(X_val_raw)
                    else:
                        model.fit(X_train_proc, y_train)
                        pred = model.predict(X_val_proc)
                        
                    # Inverse transform if target was log
                    if target_type == "log_fee_gbp":
                        pred = np.clip(pred, a_min=0, a_max=22) # Clip to ~ £3.5B to avoid exp overflow
                        pred = np.expm1(pred)
                        
                    # Clip negative predictions to a sensible minimum (e.g. 0)
                    pred = np.maximum(pred, 0)
                    
                    mae = mean_absolute_error(y_val_actual_gbp, pred)
                    rmse = np.sqrt(mean_squared_error(y_val_actual_gbp, pred))
                    r2 = r2_score(y_val_actual_gbp, pred)
                    medae = median_absolute_error(y_val_actual_gbp, pred)
                    wp = wape(y_val_actual_gbp, pred)
                    
                    results.append({
                        "experiment_id": exp["id"],
                        "train_seasons": " + ".join(exp["train"]),
                        "validation_season": exp["val"],
                        "model": model_name,
                        "feature_set": ds_name,
                        "target_type": target_type,
                        "train_rows": len(X_train_raw),
                        "validation_rows": len(X_val_raw),
                        "MAE": mae,
                        "RMSE": rmse,
                        "R2": r2,
                        "median_absolute_error": medae,
                        "WAPE": wp,
                        "random_seed": 42,
                        "config_version": "v2.0"
                    })
                    
                    # Save artifacts if this is the final holdout experiment
                    if exp["id"] == 5:
                        folder = ""
                        if "Baseline" in model_name: folder = "baseline"
                        elif "Linear" in model_name: folder = "linear"
                        elif "Ridge" in model_name: folder = "ridge"
                        elif "RandomForest" in model_name: folder = "random_forest"
                        elif "GradientBoosting" in model_name: folder = "gradient_boosting"
                        elif "XGBoost" in model_name: folder = "xgboost"
                        elif "MLP" in model_name: folder = "mlp"
                        
                        fname = f"{folder}/{model_name}_{ds_name}_{target_type}.joblib"
                        joblib.dump({
                            "model": model,
                            "preprocessor": preprocessor if "Baseline" not in model_name else None,
                            "features": features
                        }, MODELS_DIR / fname)

    # Save results
    res_df = pd.DataFrame(results)
    res_df.to_csv(DATA_DIR / "model_walk_forward_results_v2.csv", index=False)
    print("Walk-forward training completed!")
    
if __name__ == "__main__":
    run_experiments()
