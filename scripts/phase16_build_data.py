import pandas as pd
import numpy as np
from datetime import datetime
from difflib import SequenceMatcher
import json
import os

def similar(a, b):
    if pd.isna(a) or pd.isna(b): return 0
    return SequenceMatcher(None, str(a).lower(), str(b).lower()).ratio()

def main():
    print("--- Phase 16: Multi-League Data Foundation ---")
    
    # 1. Load Transfers
    print("Loading transfers...")
    transfers = pd.read_csv('data/processed/transfers_normalized.csv')
    
    # 2. Reconcile Population
    eligible_transfers = transfers[transfers['fee_gbp'] > 0].copy()
    print(f"Total eligible disclosed transfers: {len(eligible_transfers)}")
    
    # Load Master Player for Entity Resolution
    master_player = pd.read_csv('data/entity_resolution/master_player.csv')
    print(f"Total master players (after resolver fix): {len(master_player)}")
    
    # Merge transfer with master_player
    eligible_transfers = eligible_transfers.merge(master_player[['master_player_id', 'canonical_name', 'date_of_birth', 'canonical_position']], on='master_player_id', how='left')
    
    # 3. Age Repair
    eligible_transfers['transfer_date'] = pd.to_datetime(eligible_transfers['transfer_date'])
    eligible_transfers['date_of_birth'] = pd.to_datetime(eligible_transfers['date_of_birth'], errors='coerce')
    
    eligible_transfers['age_at_transfer'] = (eligible_transfers['transfer_date'] - eligible_transfers['date_of_birth']).dt.days / 365.25
    
    invalid_age_mask = (eligible_transfers['age_at_transfer'] < 15) | (eligible_transfers['age_at_transfer'] > 50)
    invalid_age_count = invalid_age_mask.sum()
    eligible_transfers.loc[invalid_age_mask, 'age_at_transfer'] = np.nan
    
    age_coverage = eligible_transfers['age_at_transfer'].notna().mean() * 100
    print(f"Age coverage: {age_coverage:.2f}% | Invalid DOBs dropped: {invalid_age_count}")
    
    # 4. T-1 Temporal Alignment & FBRef Data
    print("Loading FBRef player data...")
    fbref_players = pd.read_csv('data/raw/fbref/big5_player_standard.csv', low_memory=False)
    
    # We only need past seasons up to transfer
    # Calculate Season immediately preceding the transfer (T-1)
    # If transfer_date is in 2022 (e.g. Aug 2022), the T-1 season is 2021/2022 -> Season_End_Year = 2022
    # If transfer is Jan 2023, the completed season is 2021/2022 -> Season_End_Year = 2022
    
    def get_t1_season(date_val):
        if pd.isna(date_val): return np.nan
        y = date_val.year
        m = date_val.month
        # Typical European season ends in May/June.
        # If transfer is before July, the last COMPLETED season ended in y-1.
        # If transfer is in July or later, the last COMPLETED season ended in y.
        if m < 7:
            return y - 1
        else:
            return y

    eligible_transfers['t1_season_end_year'] = eligible_transfers['transfer_date'].apply(get_t1_season)
    
    # FBref matching
    # We will match by canonical_name (or tm_name if needed) and season
    print("Matching fbref stats...")
    
    # Optimize matching: create a dictionary of fbref players per season for fast lookup
    fbref_dict = {}
    for _, row in fbref_players.iterrows():
        s = row['Season_End_Year']
        p = str(row['Player']).lower()
        if s not in fbref_dict:
            fbref_dict[s] = []
        fbref_dict[s].append({
            'name': p,
            'minutes': row['Min_Playing'],
            'goals': row['Gls'],
            'assists': row['Ast'],
            'squad': row['Squad'],
            'comp': row['Comp']
        })
        
    t1_minutes = []
    t1_goals = []
    t1_assists = []
    t1_squads = []
    
    haaland_test = None
    
    for idx, row in eligible_transfers.iterrows():
        t1_season = row['t1_season_end_year']
        c_name = str(row['canonical_name']).lower()
        
        best_match = None
        best_score = 0
        
        if pd.notna(t1_season) and t1_season in fbref_dict:
            candidates = fbref_dict[t1_season]
            for cand in candidates:
                # exact match first
                if c_name == cand['name']:
                    best_match = cand
                    best_score = 1.0
                    break
                
                score = similar(c_name, cand['name'])
                if score > best_score:
                    best_score = score
                    best_match = cand
                    
        if best_score > 0.85 and best_match is not None:
            t1_minutes.append(best_match['minutes'])
            t1_goals.append(best_match['goals'])
            t1_assists.append(best_match['assists'])
            t1_squads.append(best_match['squad'])
            
            if 'haaland' in c_name and row['t1_season_end_year'] == 2022:
                haaland_test = {
                    'minutes': best_match['minutes'],
                    'goals': best_match['goals'],
                    'squad': best_match['squad'],
                    'comp': best_match['comp']
                }
        else:
            t1_minutes.append(np.nan)
            t1_goals.append(np.nan)
            t1_assists.append(np.nan)
            t1_squads.append(None)
            
    eligible_transfers['t1_minutes'] = t1_minutes
    eligible_transfers['t1_goals'] = t1_goals
    eligible_transfers['t1_assists'] = t1_assists
    eligible_transfers['t1_squad'] = t1_squads
    
    eligible_transfers['t1_goals_per90'] = eligible_transfers['t1_goals'] / (eligible_transfers['t1_minutes'] / 90)
    eligible_transfers['t1_assists_per90'] = eligible_transfers['t1_assists'] / (eligible_transfers['t1_minutes'] / 90)
    
    # 4.5 Merge selling club stats
    team_history = pd.read_csv('data/processed/team_history.csv')
    
    t1_selling_club_pts = []
    t1_selling_club_gd = []
    
    for _, row in eligible_transfers.iterrows():
        squad = row['t1_squad']
        t1_end = row['t1_season_end_year']
        if pd.isna(t1_end):
            t1_selling_club_pts.append(np.nan)
            t1_selling_club_gd.append(np.nan)
            continue
            
        t1_season = f"{int(t1_end)-1}_{int(t1_end)}"
        
        match = team_history[(team_history['club'] == squad) & (team_history['season_id'] == t1_season)]
        if not match.empty:
            t1_selling_club_pts.append(match['pts'].values[0])
            t1_selling_club_gd.append(match['gd'].values[0])
        else:
            t1_selling_club_pts.append(np.nan)
            t1_selling_club_gd.append(np.nan)
            
    eligible_transfers['t1_selling_club_pts'] = t1_selling_club_pts
    eligible_transfers['t1_selling_club_gd'] = t1_selling_club_gd

    print("\n--- HAALAND TEST ---")
    if haaland_test:
        print(haaland_test)
        if haaland_test['goals'] == 22 and haaland_test['minutes'] >= 1910:
            print("Haaland Pipeline Test PASSED.")
        else:
            print("Haaland Pipeline Test FAILED.")
    else:
        print("Haaland not found in matching!")

    # 5. Build Candidate Dataset
    features = [
        'transfer_id', 'master_player_id', 'canonical_name', 'transfer_date', 'season', 'selling_club', 'buying_club', 'fee_gbp',
        'age_at_transfer', 't1_minutes', 't1_goals', 't1_assists', 't1_goals_per90', 't1_assists_per90',
        't1_selling_club_pts', 't1_selling_club_gd'
    ]
    
    # We can also pull old features if needed to not lose them
    old_v4 = pd.read_csv('data/processed/transfer_features_fee_v4_candidate.csv')
    
    # Let's merge some context features from old_v4
    old_cols = ['transfer_id', 'is_foreign_import', 'position', 'is_summer_window', 'career_minutes_before_transfer', 'career_goals_before_transfer', 'log_fee_gbp']
    available_cols = [c for c in old_cols if c in old_v4.columns]
    
    candidate = eligible_transfers.merge(old_v4[available_cols], on='transfer_id', how='left')
    
    # Add Data Quality Tiers
    def get_tier(row):
        if pd.notna(row['t1_minutes']) and pd.notna(row['age_at_transfer']):
            if row['t1_minutes'] > 900:
                return 'STRONG'
            return 'USABLE'
        elif pd.notna(row['t1_minutes']) or pd.notna(row['age_at_transfer']):
            return 'LIMITED'
        return 'INSUFFICIENT'
        
    candidate['data_quality_tier'] = candidate.apply(get_tier, axis=1)
    
    # Add temporal valid flag
    candidate['temporal_valid'] = candidate['t1_minutes'].notna().astype(int)
    
    out_cols = [c for c in candidate.columns if c not in ['t1_season_end_year', 'date_of_birth', 'canonical_position']]
    candidate = candidate[out_cols]
    
    candidate.to_csv('data/processed/transfer_features_fee_v4_candidate.csv', index=False)
    print("Saved candidate dataset to data/processed/transfer_features_fee_v4_candidate.csv")
    
    print("\n--- TIER SUMMARY ---")
    print(candidate['data_quality_tier'].value_counts())

if __name__ == "__main__":
    main()
