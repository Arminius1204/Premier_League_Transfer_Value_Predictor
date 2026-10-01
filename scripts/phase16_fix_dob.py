import pandas as pd
import numpy as np

def fix_dob():
    print("Fixing Date of Birth...")
    
    # Load transfers and eordo to map transfer -> age
    transfers = pd.read_csv('data/processed/transfers_normalized.csv')
    eordo = pd.read_csv('data/raw/transfermarkt_eordo_2018_2025.csv')
    
    eordo['season_id'] = eordo['season'].apply(lambda x: f"{x}_{x+1}")
    eordo['match_name'] = eordo['player_name'].str.lower().str.replace(' ', '')
    
    master = pd.read_csv('data/entity_resolution/master_player.csv')
    
    # Create a mapping from master_player_id -> dob
    # We match transfers to eordo to get age, then calculate dob
    transfers['transfer_date'] = pd.to_datetime(transfers['transfer_date'])
    
    merged = transfers.merge(master[['master_player_id', 'canonical_name']], on='master_player_id', how='left')
    merged['match_name'] = merged['canonical_name'].str.lower().str.replace(' ', '')
    
    merged = merged.merge(eordo[['season_id', 'match_name', 'age']], on=['season_id', 'match_name'], how='left')
    
    dob_map = {}
    for idx, row in merged.iterrows():
        pid = row['master_player_id']
        age = row['age']
        t_date = row['transfer_date']
        
        if pd.notna(age) and pd.notna(t_date) and pid not in dob_map:
            # Approximate DOB: transfer_date - age years
            # For simplicity, assume birthday is Jan 1st of that year
            approx_year = t_date.year - int(age)
            dob = f"{approx_year}-01-01"
            dob_map[pid] = dob
            
    # Also check fbref for Born
    fbref = pd.read_csv('data/raw/fbref/big5_player_standard.csv', low_memory=False)
    fbref_born = {}
    for _, row in fbref.iterrows():
        name = str(row['Player']).lower().replace(' ', '')
        born = row['Born']
        if pd.notna(born):
            fbref_born[name] = str(int(born)) + "-01-01"
            
    # Update master_player.csv
    master['date_of_birth'] = master['date_of_birth'].astype(object)
    for idx, row in master.iterrows():
        pid = row['master_player_id']
        cname = str(row['canonical_name']).lower().replace(' ', '')
        if pid in dob_map:
            master.at[idx, 'date_of_birth'] = dob_map[pid]
        elif cname in fbref_born:
            master.at[idx, 'date_of_birth'] = fbref_born[cname]
            
    master.to_csv('data/entity_resolution/master_player.csv', index=False)
    print(f"Updated DOB for {master['date_of_birth'].notna().sum()} players.")

if __name__ == "__main__":
    fix_dob()
