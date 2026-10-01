import pandas as pd
import numpy as np
from pathlib import Path
import joblib
import warnings as _warnings


# Non-negative features that must never be < 0
_NON_NEGATIVE_FEATURES = frozenset([
    "t1_minutes", "t1_goals", "t1_assists",
    "t1_goals_per90", "t1_assists_per90", "t1_bps_per90",
    "age_at_transfer", "career_minutes_before_transfer",
    "career_goals_before_transfer", "two_season_avg_minutes",
    "two_season_avg_goals", "previous_transfer_fee_gbp",
    "previous_transfer_count", "t1_bps", "selling_club_pts_t1",
])

# Hard domain bounds for specific features
_HARD_BOUNDS = {
    "age_at_transfer": (15, 50),
    "t1_minutes": (0, 5000),
    "t1_goals_per90": (0, 5.0),
    "t1_assists_per90": (0, 5.0),
    "t1_bps_per90": (0, 200.0),
    "selling_club_pts_t1": (0, 120),
}


class WhatIfSimulator:
    def __init__(self, data_path: Path, models_dir: Path):
        self.df = pd.read_csv(data_path)

        # Merge canonical names
        players = pd.read_csv(data_path.parent / "players.csv")
        self.df = self.df.merge(
            players[["master_player_id", "canonical_name"]],
            on="master_player_id",
            how="left",
        )

        # Load Frozen Phase 12 Artifacts
        self.preprocessor = joblib.load(
            models_dir / "preprocessors/final_preprocessor.joblib"
        )
        self.meta = joblib.load(models_dir / "ensemble/ensemble_metadata.joblib")

        self.models = {
            "Ridge": joblib.load(models_dir / "selected_models/Ridge_final.joblib"),
            "RandomForest": joblib.load(
                models_dir / "selected_models/RandomForest_final.joblib"
            ),
            "XGBoost": joblib.load(
                models_dir / "selected_models/XGBoost_final.joblib"
            ),
        }
        self.weights = self.meta["weights"]
        self.features = self.meta["features"]
        self.q_80 = self.meta["q_80"]
        self.q_90 = self.meta["q_90"]

        # Build Reference Distribution for OOD Detection (from ALL historical data)
        self.ood_bounds = {}
        for f in self.features:
            if pd.api.types.is_numeric_dtype(self.df[f]):
                col = self.df[f].dropna()
                if len(col) > 0:
                    self.ood_bounds[f] = {
                        "min": float(col.min()),
                        "max": float(col.max()),
                        "p5": float(col.quantile(0.05)),
                        "p95": float(col.quantile(0.95)),
                    }

    # ------------------------------------------------------------------
    # OOD detection — returns structured output
    # ------------------------------------------------------------------
    def _check_ood(self, scenario_dict: dict) -> dict:
        """
        Check every feature in *scenario_dict* against historical bounds.
        Returns a structured dict:
            ood: bool
            ood_features: list[str]
            warnings: list[str]
        """
        ood_features = []
        warn_msgs = []
        for f, val in scenario_dict.items():
            if f in self.ood_bounds and pd.notnull(val):
                b = self.ood_bounds[f]
                if val < b["min"] or val > b["max"]:
                    ood_features.append(f)
                    warn_msgs.append(
                        f"OOD: {f}={val} outside historical range "
                        f"[{b['min']}, {b['max']}]"
                    )
        return {
            "ood": len(ood_features) > 0,
            "ood_features": ood_features,
            "warnings": warn_msgs,
        }

    # ------------------------------------------------------------------
    # Domain validation — rejects impossible inputs before inference
    # ------------------------------------------------------------------
    @staticmethod
    def _validate_scenario(feature_name: str, value):
        """Raise ValueError if *value* violates hard domain constraints."""
        if feature_name in _NON_NEGATIVE_FEATURES and value < 0:
            raise ValueError(
                f"Feature '{feature_name}' cannot be negative. Got {value}."
            )
        if feature_name in _HARD_BOUNDS:
            lo, hi = _HARD_BOUNDS[feature_name]
            if value < lo or value > hi:
                raise ValueError(
                    f"Feature '{feature_name}' value {value} outside "
                    f"realistic domain [{lo}, {hi}]."
                )

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------
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
            "upper_bound_90": pred + self.q_90,
        }

    # ------------------------------------------------------------------
    # Simulation — sensitivity analysis (NOT causal prediction)
    # ------------------------------------------------------------------
    def simulate(self, player_id: str, season: str, scenario_updates: dict):
        query_mask = (self.df["master_player_id"] == player_id) & (
            self.df["season_id"] == season
        )
        if not query_mask.any():
            raise ValueError("Player/Season combination not found.")

        baseline_row = self.df[query_mask].iloc[0]
        baseline_dict = baseline_row[self.features].to_dict()

        # Create scenario dict
        scenario_dict = baseline_dict.copy()

        # Enforce domain constraints BEFORE modifying the dict
        for k, v in scenario_updates.items():
            if k in scenario_dict:
                self._validate_scenario(k, v)
                scenario_dict[k] = v

        # Re-derive dependent features
        if "age_at_transfer" in scenario_updates and "age_squared" in scenario_dict:
            scenario_dict["age_squared"] = scenario_dict["age_at_transfer"] ** 2

        # Generate predictions
        base_pred = self.predict(baseline_dict)
        scen_pred = self.predict(scenario_dict)

        # OOD checks (structured)
        ood_result = self._check_ood(scenario_dict)

        delta_abs = scen_pred["prediction"] - base_pred["prediction"]
        delta_pct = 0.0
        if base_pred["prediction"] > 0:
            delta_pct = (delta_abs / base_pred["prediction"]) * 100

        return {
            "Baseline Prediction": base_pred["prediction"],
            "Baseline Interval (80%)": [
                base_pred["lower_bound_80"],
                base_pred["upper_bound_80"],
            ],
            "Scenario Prediction": scen_pred["prediction"],
            "Scenario Interval (80%)": [
                scen_pred["lower_bound_80"],
                scen_pred["upper_bound_80"],
            ],
            "Absolute Change": delta_abs,
            "Percentage Change": delta_pct,
            "Changed Features": list(scenario_updates.keys()),
            # Structured OOD output
            "ood": ood_result["ood"],
            "ood_features": ood_result["ood_features"],
            "OOD Warnings": ood_result["warnings"],
            # Disclaimer
            "interpretation": "sensitivity_analysis_not_causal",
        }
