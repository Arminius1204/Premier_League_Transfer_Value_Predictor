import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os

DATA_DIR = Path("data/processed")
OUT_DIR = Path("docs/figures/feature_engineering_v2")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_plots():
    df = pd.read_csv(DATA_DIR / "transfer_features_enriched_v2.csv")
    
    # 1. Transfer fee distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(df["fee_gbp"] / 1e6, bins=50, kde=True)
    plt.title("Transfer Fee Distribution (Millions GBP)")
    plt.xlabel("Fee (Millions GBP)")
    plt.savefig(OUT_DIR / "1_fee_distribution.png")
    plt.close()
    
    # 2. Log transfer fee distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(df["log_fee_gbp"], bins=50, kde=True)
    plt.title("Log Transfer Fee Distribution")
    plt.xlabel("Log(Fee GBP)")
    plt.savefig(OUT_DIR / "2_log_fee_distribution.png")
    plt.close()
    
    # 3. Fee by season
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x="season_id", y="fee_gbp", order=sorted(df["season_id"].unique()))
    plt.title("Transfer Fee by Season")
    plt.ylabel("Fee GBP")
    plt.xticks(rotation=45)
    plt.savefig(OUT_DIR / "3_fee_by_season.png")
    plt.close()
    
    # 4. Fee by position
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x="position", y="fee_gbp")
    plt.title("Transfer Fee by Position")
    plt.ylabel("Fee GBP")
    plt.savefig(OUT_DIR / "4_fee_by_position.png")
    plt.close()
    
    # 5. Age vs fee
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x="age_at_transfer", y="fee_gbp", alpha=0.5)
    plt.title("Age at Transfer vs Fee")
    plt.ylabel("Fee GBP")
    plt.savefig(OUT_DIR / "5_age_vs_fee.png")
    plt.close()
    
    # 6. goals_per90 vs fee
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x="t1_goals_per90", y="fee_gbp", alpha=0.5)
    plt.title("Previous Season Goals/90 vs Fee")
    plt.ylabel("Fee GBP")
    plt.savefig(OUT_DIR / "6_goals_p90_vs_fee.png")
    plt.close()
    
    # 7. bps_per90 vs fee (Proxy for xG/Performance)
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x="t1_bps_per90", y="fee_gbp", alpha=0.5)
    plt.title("Previous Season BPS/90 vs Fee")
    plt.ylabel("Fee GBP")
    plt.savefig(OUT_DIR / "7_bps_p90_vs_fee.png")
    plt.close()
    
    # 8. club strength vs fee
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x="selling_club_pts_t1", y="fee_gbp", alpha=0.5)
    plt.title("Selling Club Points (T-1) vs Fee")
    plt.ylabel("Fee GBP")
    plt.savefig(OUT_DIR / "8_club_strength_vs_fee.png")
    plt.close()
    
    # 9. missingness overview
    plt.figure(figsize=(12, 8))
    missing = df.isnull().mean() * 100
    missing = missing[missing > 0].sort_values(ascending=True)
    if not missing.empty:
        missing.plot(kind="barh")
        plt.title("Missing Data Percentage by Feature")
        plt.xlabel("% Missing")
        plt.tight_layout()
        plt.savefig(OUT_DIR / "9_missingness.png")
    plt.close()
    
    # 10. feature correlation heatmap
    plt.figure(figsize=(14, 12))
    numeric_df = df.select_dtypes(include=[np.number])
    corr = numeric_df.corr()
    sns.heatmap(corr, cmap="coolwarm", center=0, annot=False)
    plt.title("Feature Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "10_correlation_heatmap.png")
    plt.close()
    
    print("Plots generated in docs/figures/feature_engineering_v2/")

if __name__ == "__main__":
    generate_plots()
