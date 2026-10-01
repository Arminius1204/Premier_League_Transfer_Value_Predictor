import pandas as pd
players = pd.read_csv('data/processed/players.csv')
for _, row in players.iterrows():
    name = str(row['canonical_name']).lower()
    if 'brahim' in name or 'arkic' in name or 'sarkic' in name:
        print(f"{name.encode('ascii', 'ignore').decode()} -> {row['master_player_id']}")
