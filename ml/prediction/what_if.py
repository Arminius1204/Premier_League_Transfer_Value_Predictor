import pandas as pd
import numpy as np
from pathlib import Path
import joblib
import warnings

class WhatIfSimulator:
    def __init__(self, data_path: Path, models_dir: Path):
        self.df = pd.read_csv(data_path)
        
        # Merge canonical names
        players = pd.read_csv(data_path.parent / "players.csv")
        self.df = self.df.merge(players[["master_player_id", "canonical_name"]], on="master_player_id", how="left")
        
        # Load Frozen Phase 12 Artifacts
        self.preprocessor = joblib.load(models_dir / "preprocessors/final_preprocessor.joblib")
        self.meta = joblib.load(models_dir / "ensemble/ensemble_metadata.joblib")
        
        self.models = {
            "Ridge": joblib.load(models_dir / "selected_models/Ridge_final.joblib"),
            "RandomForest": joblib.load(models_dir / "selected_models/RandomForest_final.joblib"),
            "XGBoost": joblib.load(models_dir / "selected_models/XGBoost_final.joblib")
        }
        self.weights = self.meta["weights"]
        self.features = self.meta["features"]
        self.q_80 = self.meta["q_80"]
        self.q_90 = self.meta["q_90"]
        
        # Build Reference Distribution for OOD Detection (from ALL historical data)
        self.ood_bounds = {}
        for f in self.features:
            if pd.api.types.is_numeric_dtype(self.df[f]):
                self.ood_bounds[f] = {
                    "min": self.df[f].min(),
                    "max": self.df[f].max()
                }

    def _check_ood(self, scenario_dict):
        warnings = []
        for f, val in scenario_dict.items():
            if f in self.ood_bounds and pd.notnull(val):
                b = self.ood_bounds[f]
                if val < b["min"] or val > b["max"]:
                    warnings.append(
                        f"WARNING: OOD Feature - {f} ({val}) is outside historical reference bounds ({b['min']} to {b['max']})."
                    )
        return warnings

    def predict(self, feature_dict):
        # Convert dict to exactly the format expected by the preprocessor
        row_df = pd.DataFrame([feature_dict])[self.features]
        X_proc = self.preprocessor.transform(row_df)
        
        pred = 0.0
        for m_name, model in self.models.items():
            m_pred = np.maximum(model.predict(X_proc)[0], 0)
            pred += m_pred * self.weights[m_name]
            
        return {
            "prediction": pred,
            "lower_bound_80": max(pred - self.q_80, 0),
            "upper_bound_80": pred + self.q_80,
            "lower_bound_90": max(pred - self.q_90, 0),
            "upper_bound_90": pred + self.q_90
        }

    def simulate(self, player_id: str, season: str, scenario_updates: dict):
        query_mask = (self.df['master_player_id'] == player_id) & (self.df['season_id'] == season)
        if not query_mask.any():
            raise ValueError("Player/Season combination not found.")
            
        baseline_row = self.df[query_mask].iloc[0]
        baseline_dict = baseline_row[self.features].to_dict()
        
        # Create scenario dict
        scenario_dict = baseline_dict.copy()
        for k, v in scenario_updates.items():
            if k in scenario_dict:
                scenario_dict[k] = v
                
        # Generate predictions
        base_pred = self.predict(baseline_dict)
        scen_pred = self.predict(scenario_dict)
        
        # OOD checks
        ood_warnings = self._check_ood(scenario_dict)
        
        delta_abs = scen_pred["prediction"] - base_pred["prediction"]
        delta_pct = 0.0
        if base_pred["prediction"] > 0:
            delta_pct = (delta_abs / base_pred["prediction"]) * 100
            
        return {
            "Baseline Prediction": base_pred["prediction"],
            "Baseline Interval (80%)": [base_pred["lower_bound_80"], base_pred["upper_bound_80"]],
            "Scenario Prediction": scen_pred["prediction"],
            "Scenario Interval (80%)": [scen_pred["lower_bound_80"], scen_pred["upper_bound_80"]],
            "Absolute Change": delta_abs,
            "Percentage Change": delta_pct,
            "Changed Features": list(scenario_updates.keys()),
            "OOD Warnings": ood_warnings
        }
