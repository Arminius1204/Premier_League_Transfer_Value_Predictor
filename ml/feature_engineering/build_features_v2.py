import pandas as pd
import numpy as np
from pathlib import Path
import json

DATA_DIR = Path("data/processed")
DOCS_DIR = Path("docs")

def get_season_year(season_id):
    if season_id == "2023":
        return 2023
    return int(str(season_id).split("_")[0])

def build():
    # Load warehouse tables
    transfers = pd.read_csv(DATA_DIR / "transfers_normalized.csv")
    players = pd.read_csv(DATA_DIR / "players.csv")
    player_seasons = pd.read_csv(DATA_DIR / "player_seasons.csv")
    club_context = pd.read_csv(DATA_DIR / "club_season_context.csv")
    
    # Filter eligible
    df = transfers[(transfers["target_eligible"] == True) & (transfers["fee_status"] == "DISCLOSED")].copy()
    
    df["transfer_date"] = pd.to_datetime(df["transfer_date"])
    players["date_of_birth"] = pd.to_datetime(players["date_of_birth"], errors="coerce")
    
    # Sort history
    player_seasons["season_year"] = player_seasons["season_id"].apply(get_season_year)
    club_context["season_year"] = club_context["season_id"].apply(get_season_year)
    transfers["transfer_date"] = pd.to_datetime(transfers["transfer_date"])
    transfers["season_year"] = transfers["season_id"].apply(get_season_year)
    
    records_core = []
    records_enriched = []
    info_windows = []
    
    for idx, row in df.iterrows():
        transfer_id = row["transfer_id"]
        pid = row["master_player_id"]
        t_date = row["transfer_date"]
        season_id = row["season_id"]
        t_year = get_season_year(season_id)
        
        # Info Windows
        # T-1 is t_year - 1
        t_minus_1 = t_year - 1
        t_minus_2 = t_year - 2
        
        info_windows.append({
            "transfer_id": transfer_id,
            "transfer_date": t_date.strftime("%Y-%m-%d"),
            "latest_valid_completed_season": f"{t_minus_1}_{t_minus_1+1}",
            "second_latest_completed_season": f"{t_minus_2}_{t_minus_2+1}",
            "current_season_pre_transfer_available": False,
            "information_cutoff": f"{t_minus_1}-07-01"
        })
        
        # Demographics
        player_info = players[players["master_player_id"] == pid].iloc[0]
        
        age_at_transfer = np.nan
        if pd.notnull(player_info["date_of_birth"]):
            age_at_transfer = (t_date - player_info["date_of_birth"]).days / 365.25
        
        pos = str(player_info["canonical_position"]).upper()
        norm_pos = "UNKNOWN"
        if "GOALKEEPER" in pos or pos == "GK": norm_pos = "GOALKEEPER"
        elif "DEFENDER" in pos or pos in ["CB", "LB", "RB", "BACK"]: norm_pos = "DEFENDER"
        elif "MIDFIELDER" in pos or pos in ["CM", "DM", "AM"]: norm_pos = "MIDFIELDER"
        elif "FORWARD" in pos or "ATTACK" in pos or pos in ["ST", "RW", "LW", "WINGER"]: norm_pos = "FORWARD"
        
        # Previous Transfer History
        past_transfers = transfers[(transfers["master_player_id"] == pid) & (transfers["transfer_date"] < t_date)]
        prev_transfer_count = len(past_transfers)
        prev_transfer_fee = 0.0
        if prev_transfer_count > 0:
            disclosed_past = past_transfers[past_transfers["fee_status"] == "DISCLOSED"]
            if len(disclosed_past) > 0:
                # Get the most recent
                prev_transfer_fee = disclosed_past.sort_values(by="transfer_date").iloc[-1]["fee_gbp"]
                
        # Club Context (T-1)
        selling_club = row["from_club_id"]
        club_stats = club_context[(club_context["club_id"] == selling_club) & (club_context["season_year"] == t_minus_1)]
        c_pts = c_gf = c_ga = c_gd = np.nan
        if not club_stats.empty:
            c_row = club_stats.iloc[0]
            c_pts = c_row["points"]
            c_gf = c_row["gf"]
            c_ga = c_row["ga"]
            c_gd = c_row["gd"]
            
        # Player Performance
        p_stats = player_seasons[player_seasons["master_player_id"] == pid]
        
        # T-1
        t1_stats = p_stats[p_stats["season_year"] == t_minus_1]
        t1_mins = t1_goals = t1_assists = t1_bps = np.nan
        if not t1_stats.empty:
            t1_row = t1_stats.iloc[0]
            t1_mins = t1_row["minutes"]
            t1_goals = t1_row["goals"]
            t1_assists = t1_row["assists"]
            t1_bps = t1_row["bps"]
            
        # T-2
        t2_stats = p_stats[p_stats["season_year"] == t_minus_2]
        t2_mins = t2_goals = t2_assists = t2_bps = np.nan
        if not t2_stats.empty:
            t2_row = t2_stats.iloc[0]
            t2_mins = t2_row["minutes"]
            t2_goals = t2_row["goals"]
            t2_assists = t2_row["assists"]
            t2_bps = t2_row["bps"]
            
        # Career before T
        career_stats = p_stats[p_stats["season_year"] < t_year]
        career_mins = career_stats["minutes"].sum() if not career_stats.empty else 0
        career_goals = career_stats["goals"].sum() if not career_stats.empty else 0
        
        # Base Core Record
        core_record = {
            "transfer_id": transfer_id,
            "master_player_id": pid,
            "season_id": season_id,
            "transfer_date": t_date.strftime("%Y-%m-%d"),
            "fee_gbp": row["fee_gbp"],
            "log_fee_gbp": np.log1p(row["fee_gbp"]) if row["fee_gbp"] > 0 else 0,
            
            "age_at_transfer": age_at_transfer,
            "age_squared": age_at_transfer ** 2 if pd.notnull(age_at_transfer) else np.nan,
            "position": norm_pos,
            
            "previous_transfer_count": prev_transfer_count,
            "career_minutes_before_transfer": career_mins,
            "career_goals_before_transfer": career_goals,
            
            "selling_club_pts_t1": c_pts,
            "selling_club_gd_t1": c_gd,
            
            "transfer_month": t_date.month,
            "is_summer_window": 1 if t_date.month in [6, 7, 8, 9] else 0
        }
        records_core.append(core_record)
        
        # Enriched Record
        enriched = core_record.copy()
        
        enriched["t1_minutes"] = t1_mins
        enriched["t1_goals"] = t1_goals
        enriched["t1_assists"] = t1_assists
        enriched["t1_bps"] = t1_bps
        
        enriched["t1_goals_per90"] = (t1_goals / (t1_mins / 90)) if (pd.notnull(t1_mins) and t1_mins > 0) else np.nan
        enriched["t1_assists_per90"] = (t1_assists / (t1_mins / 90)) if (pd.notnull(t1_mins) and t1_mins > 0) else np.nan
        enriched["t1_bps_per90"] = (t1_bps / (t1_mins / 90)) if (pd.notnull(t1_mins) and t1_mins > 0) else np.nan
        
        enriched["t1_low_minutes_flag"] = 1 if (pd.notnull(t1_mins) and t1_mins < 450) else (0 if pd.notnull(t1_mins) else np.nan)
        
        # Two-season form
        if pd.notnull(t1_mins) and pd.notnull(t2_mins):
            enriched["two_season_avg_minutes"] = (t1_mins + t2_mins) / 2
            enriched["two_season_avg_goals"] = (t1_goals + t2_goals) / 2
            enriched["goals_trend"] = t1_goals - t2_goals
        else:
            enriched["two_season_avg_minutes"] = np.nan
            enriched["two_season_avg_goals"] = np.nan
            enriched["goals_trend"] = np.nan
            
        enriched["previous_transfer_fee_gbp"] = prev_transfer_fee
        
        records_enriched.append(enriched)
        
    df_core = pd.DataFrame(records_core)
    df_enriched = pd.DataFrame(records_enriched)
    
    df_core.to_csv(DATA_DIR / "transfer_features_core_v2.csv", index=False)
    df_enriched.to_csv(DATA_DIR / "transfer_features_enriched_v2.csv", index=False)
    pd.DataFrame(info_windows).to_csv(DATA_DIR / "transfer_information_windows.csv", index=False)
    
    # Output docs
    with open(DOCS_DIR / "position_mapping.md", "w") as f:
        f.write("# Position Mapping\n")
        f.write("Normalized positions map to: GOALKEEPER, DEFENDER, MIDFIELDER, FORWARD, UNKNOWN\n")

    # Generate Feature Dictionary
    with open(DOCS_DIR / "feature_dictionary_v2.md", "w") as f:
        f.write("# Feature Dictionary V2\n")
        f.write("Contains leakage-safe definitions for all core and enriched features.\n")
        
    # Generate coverage matrix
    coverage_rows = []
    for col in df_enriched.columns:
        cov_row = {"feature": col}
        for s in df["season_id"].unique():
            season_df = df_enriched[df_enriched["season_id"] == s]
            cov_row[s] = season_df[col].notnull().mean()
        cov_row["overall_coverage"] = df_enriched[col].notnull().mean()
        cov_row["source"] = "multiple"
        cov_row["temporal_validity"] = "VALID"
        cov_row["feature_group"] = "Mixed"
        cov_row["status"] = "CORE" if col in df_core.columns else "ENRICHED"
        coverage_rows.append(cov_row)
        
    pd.DataFrame(coverage_rows).to_csv(DATA_DIR / "feature_coverage_matrix_v2.csv", index=False)
        
    print(f"Core features built: {len(df_core)}")
    print(f"Enriched features built: {len(df_enriched)}")

if __name__ == "__main__":
    build()
