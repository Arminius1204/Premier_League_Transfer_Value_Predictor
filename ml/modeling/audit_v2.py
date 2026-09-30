import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

DATA_DIR = Path("data/processed")
FIG_DIR = Path("docs/figures/modeling_v2")
DOCS_DIR = Path("docs")
FIG_DIR.mkdir(parents=True, exist_ok=True)

def run_audit():
    core = pd.read_csv(DATA_DIR / "transfer_features_core_v2.csv")
    enriched = pd.read_csv(DATA_DIR / "transfer_features_enriched_v2.csv")
    
    # 1. Audit Report
    with open(DOCS_DIR / "phase11_modeling_data_audit.md", "w") as f:
        f.write("# Phase 11 Modeling Data Audit\n\n")
        
        for name, df in [("Core", core), ("Enriched", enriched)]:
            f.write(f"## {name} Dataset\n")
            f.write(f"- Rows: {len(df)}\n")
            f.write(f"- Columns: {len(df.columns)}\n")
            num_cols = df.select_dtypes(include=np.number).columns
            cat_cols = df.select_dtypes(exclude=np.number).columns
            f.write(f"- Numeric features: {len(num_cols)}\n")
            f.write(f"- Categorical features: {len(cat_cols)}\n")
            f.write(f"- Duplicate transfer IDs: {df['transfer_id'].duplicated().sum()}\n")
            
            f.write("\n### Missingness (%)\n")
            missing = df.isnull().mean() * 100
            for col, pct in missing[missing > 0].items():
                f.write(f"- {col}: {pct:.1f}%\n")
                
            f.write("\n### Constant Columns\n")
            const_cols = [c for c in df.columns if df[c].nunique() <= 1]
            f.write(f"- {const_cols if const_cols else 'None'}\n\n")
            
        f.write("## Season Breakdown\n")
        f.write(core.groupby("season_id").size().to_string() + "\n")

    # 2. Target Distribution
    stats = []
    for s in core["season_id"].unique():
        s_df = core[core["season_id"] == s]
        fee = s_df["fee_gbp"]
        log_fee = s_df["log_fee_gbp"]
        stats.append({
            "season": s,
            "count": len(fee),
            "fee_mean": fee.mean(),
            "fee_median": fee.median(),
            "fee_std": fee.std(),
            "fee_min": fee.min(),
            "fee_max": fee.max(),
            "fee_p25": fee.quantile(0.25),
            "fee_p75": fee.quantile(0.75),
            "fee_skew": fee.skew()
        })
    pd.DataFrame(stats).to_csv(DATA_DIR / "target_distribution_by_season.csv", index=False)
    
    plt.figure(figsize=(10,6))
    sns.histplot(core["fee_gbp"], kde=True)
    plt.title("Fee Distribution")
    plt.savefig(FIG_DIR / "fee_distribution.png")
    plt.close()
    
    plt.figure(figsize=(10,6))
    sns.histplot(core["log_fee_gbp"], kde=True)
    plt.title("Log Fee Distribution")
    plt.savefig(FIG_DIR / "log_fee_distribution.png")
    plt.close()
    
    plt.figure(figsize=(10,6))
    sns.boxplot(data=core, x="season_id", y="fee_gbp", order=sorted(core["season_id"].unique()))
    plt.title("Fee by Season")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "fee_boxplot_by_season.png")
    plt.close()

    # 4. Sample Size Per Window
    seasons = sorted(core["season_id"].unique())
    temporal_splits = []
    for i in range(1, len(seasons)):
        train_seasons = seasons[:i]
        val_season = seasons[i]
        train_rows = len(core[core["season_id"].isin(train_seasons)])
        val_rows = len(core[core["season_id"] == val_season])
        temporal_splits.append({
            "experiment": f"Exp_{i}",
            "train_seasons": " + ".join(train_seasons),
            "val_season": val_season,
            "train_rows": train_rows,
            "val_rows": val_rows
        })
    pd.DataFrame(temporal_splits).to_csv(DATA_DIR / "temporal_split_summary_v2.csv", index=False)
    
    # 5. Player Repetition Audit
    with open(DOCS_DIR / "player_repetition_audit_v2.md", "w") as f:
        f.write("# Player Repetition Audit\n\n")
        f.write(f"- Unique players: {core['master_player_id'].nunique()}\n")
        f.write(f"- Total transfers: {len(core)}\n")
        vc = core['master_player_id'].value_counts()
        f.write(f"- Repeated players (>= 2 transfers): {len(vc[vc >= 2])}\n")
        f.write(f"- Maximum transfers per player: {vc.max()}\n")
        
        # Cross-temporal leak check
        multi_temp = 0
        for pid in vc[vc >= 2].index:
            s_list = core[core["master_player_id"] == pid]["season_id"].unique()
            if len(s_list) > 1:
                multi_temp += 1
        f.write(f"- Players appearing across multiple seasons: {multi_temp}\n")
        f.write("\n*Implication: Since master_player_id is NOT a feature, the model cannot memorize identities. However, correlated traits (like position, demographics) might be seen. This is realistic.*")

if __name__ == "__main__":
    run_audit()
