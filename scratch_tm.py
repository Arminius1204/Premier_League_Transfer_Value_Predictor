import pandas as pd
from pathlib import Path
import csv

raw_dir = Path('data/parsed/transfermarkt')
raw_files = list(raw_dir.glob('transfermarkt_parsed_*.csv'))

transfer_clubs = {}
for f in raw_files:
    df = pd.read_csv(f)
    for _, row in df.iterrows():
        parts = str(row['raw_row_text']).split('|')
        if len(parts) >= 5:
            from_club = parts[3].strip()
            to_club = parts[4].strip()
            transfer_clubs[row['transfer_id']] = {'from': from_club, 'to': to_club}
        else:
            print(f'Warning: malformed row {row["raw_row_text"]}')

print(f'Parsed {len(transfer_clubs)} transfers')
print('Example:', list(transfer_clubs.items())[0])
