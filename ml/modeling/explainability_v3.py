import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import joblib

DATA_DIR = Path("data/processed")
FIG_DIR = Path("docs/figures/phase12")
MODELS_DIR = Path("models/v3")
DOCS_DIR = Path("docs")
FIG_DIR.mkdir(parents=True, exist_ok=True)

def run_explainability():
    # Load final preprocessor & Ridge model to get coefficients
    preprocessor = joblib.load(MODELS_DIR / "preprocessors/final_preprocessor.joblib")
    ridge_model = joblib.load(MODELS_DIR / "selected_models/Ridge_final.joblib")
    xgb_model = joblib.load(MODELS_DIR / "selected_models/XGBoost_final.joblib")
    meta = joblib.load(MODELS_DIR / "ensemble/ensemble_metadata.joblib")
    
    # Preprocessor feature names
    num_imputer = preprocessor.named_transformers_['num'].named_steps['imputer']
    num_raw_features = preprocessor.transformers_[0][2]
    num_features = list(num_imputer.get_feature_names_out(num_raw_features))
    
    # Categorical names
    cat_encoder = preprocessor.named_transformers_['cat'].named_steps['onehot']
    cat_raw_features = preprocessor.transformers_[1][2]
    cat_features = list(cat_encoder.get_feature_names_out(cat_raw_features))
    
    all_feature_names = num_features + cat_features
    
    # 1. Ridge Coefficients
    coef_df = pd.DataFrame({
        "Feature": all_feature_names,
        "Coefficient": ridge_model.coef_
    }).sort_values(by="Coefficient", key=abs, ascending=False)
    
    plt.figure(figsize=(10, 8))
    sns.barplot(data=coef_df.head(20), x="Coefficient", y="Feature", palette="coolwarm")
    plt.title("Top 20 Ridge Model Coefficients (Predictive Association)")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "ridge_coefficients.png")
    plt.close()

    # 2. XGBoost Feature Importance
    xgb_imp = pd.DataFrame({
        "Feature": all_feature_names,
        "Importance": xgb_model.feature_importances_
    }).sort_values(by="Importance", ascending=False)
    
    plt.figure(figsize=(10, 8))
    sns.barplot(data=xgb_imp.head(20), x="Importance", y="Feature", palette="viridis")
    plt.title("Top 20 XGBoost Feature Importances")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "xgboost_importance.png")
    plt.close()

    # 3. Model-Market Discrepancy (Holdout)
    holdout = pd.read_csv(DATA_DIR / "final_holdout_predictions_v3.csv")
    
    # Merge context to get player details
    players = pd.read_csv(DATA_DIR / "players.csv")
    holdout = holdout.merge(players[["master_player_id", "canonical_name"]], on="master_player_id", how="left")
    
    holdout["model_market_gap"] = holdout["predicted_fee"] - holdout["fee_gbp"]
    holdout["absolute_error"] = holdout["model_market_gap"].abs()
    
    plt.figure(figsize=(10, 6))
    sns.histplot(holdout["model_market_gap"] / 1e6, kde=True, bins=30)
    plt.title("Model-Market Discrepancy (£M)")
    plt.xlabel("Predicted - Actual (£M)")
    plt.axvline(0, color="red", linestyle="--")
    plt.savefig(FIG_DIR / "model_market_discrepancy.png")
    plt.close()

    # Coverage verification
    cov_80 = holdout["covered_80"].mean()
    cov_90 = holdout["covered_90"].mean()
    
    # Error by confidence/interval width
    holdout["interval_width"] = holdout["upper_bound_80"] - holdout["lower_bound_80"]
    # Bins
    holdout["uncertainty_tier"] = pd.qcut(holdout["interval_width"], q=3, labels=False, duplicates='drop')

    
    tier_errors = holdout.groupby("uncertainty_tier")["absolute_error"].mean()
    
    plt.figure(figsize=(8, 6))
    tier_errors.plot(kind="bar", color="skyblue")
    plt.title("Mean Absolute Error by Uncertainty Tier")
    plt.ylabel("MAE (£)")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "error_by_uncertainty.png")
    plt.close()

    # High Error Cases
    high_errors = holdout.sort_values(by="absolute_error", ascending=False).head(10)
    
    with open(DOCS_DIR / "phase12_error_case_analysis.md", "w") as f:
        f.write("# Phase 12 High-Error Case Analysis\n\n")
        f.write("This analysis identifies the largest absolute errors on the frozen 2023/24 test set. These cases were not used to tune the model.\n\n")
        f.write(f"**Empirical 80% Coverage:** {cov_80*100:.1f}%\n")
        f.write(f"**Empirical 90% Coverage:** {cov_90*100:.1f}%\n\n")
        
        for idx, row in high_errors.iterrows():
            f.write(f"### {row['canonical_name']} (ID: {row['master_player_id']})\n")
            f.write(f"- **Actual Fee:** £{row['fee_gbp']/1e6:.1f}M\n")
            f.write(f"- **Predicted Fee:** £{row['predicted_fee']/1e6:.1f}M\n")
            f.write(f"- **Gap (Predicted - Actual):** £{row['model_market_gap']/1e6:.1f}M\n")
            f.write(f"- **80% Prediction Interval:** [£{row['lower_bound_80']/1e6:.1f}M, £{row['upper_bound_80']/1e6:.1f}M]\n")
            
            if row["model_market_gap"] > 0:
                f.write("- **Model Position:** ABOVE MARKET FEE\n\n")
            else:
                f.write("- **Model Position:** BELOW MARKET FEE\n\n")

if __name__ == "__main__":
    run_explainability()
