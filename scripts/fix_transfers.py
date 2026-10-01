import pandas as pd
from bs4 import BeautifulSoup
import re
from pathlib import Path
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ml.entity_resolution.club_resolver import ClubResolver

def get_club_mappings_from_html():
    mappings = {}
    for file in Path('data/raw/transfermarkt').glob('*.html'):
        season = file.name.split('pl_')[1].replace('.html', '')
        with open(file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        for box in soup.find_all('div', class_='box'):
            header = box.find('h2', class_='content-box-headline')
            if not header: continue
            base_club = header.text.strip()
            
            responsive_tables = box.find_all('div', class_='responsive-table')
            if len(responsive_tables) == 2:
                for table, direction in [(responsive_tables[0], 'in'), (responsive_tables[1], 'out')]:
                    for row in table.find_all('tr'):
                        club_link = row.find('a', href=re.compile(r'/verein/'))
                        other_club = club_link.get('title', club_link.text) if club_link else 'UNKNOWN'
                        
                        fee_link = row.find('a', href=re.compile(r'/transfer_id/'))
                        if fee_link:
                            tid_match = re.search(r'/transfer_id/(\d+)', fee_link['href'])
                            if tid_match:
                                tid = tid_match.group(1)
                                if direction == 'in':
                                    from_club = other_club
                                    to_club = base_club
                                else:
                                    from_club = base_club
                                    to_club = other_club
                                mappings[tid] = {'from_club': from_club, 'to_club': to_club}
    return mappings

def fix_transfers():
    mappings = get_club_mappings_from_html()
    
    # Load transfermarkt_parsed to map transfer_id to source_transfer_id
    parsed_transfers = []
    for file in Path('data/parsed/transfermarkt').glob('transfermarkt_parsed_*.csv'):
        parsed_transfers.append(pd.read_csv(file))
    parsed_df = pd.concat(parsed_transfers)
    
    tid_map = {}
    for _, row in parsed_df.iterrows():
        source_tid = str(row['source_transfer_id'])
        if source_tid in mappings:
            tid_map[row['transfer_id']] = mappings[source_tid]
    canonical_mapping = {
        "Arsenal": "Arsenal",
        "Aston Villa": "Aston Villa",
        "Bournemouth": "Bournemouth",
        "Brentford": "Brentford",
        "Brighton": "Brighton",
        "Burnley": "Burnley",
        "Chelsea": "Chelsea",
        "Crystal Palace": "Crystal Palace",
        "Everton": "Everton",
        "Fulham": "Fulham",
        "Liverpool": "Liverpool",
        "Luton": "Luton Town",
        "Luton Town": "Luton Town",
        "Man City": "Manchester City",
        "Manchester City": "Manchester City",
        "Man United": "Manchester United",
        "Manchester United": "Manchester United",
        "Man Utd": "Manchester United",
        "Newcastle": "Newcastle United",
        "Newcastle Utd": "Newcastle United",
        "Nott'm Forest": "Nottingham Forest",
        "Nottingham Forest": "Nottingham Forest",
        "Sheffield Utd": "Sheffield United",
        "Sheffield United": "Sheffield United",
        "Tottenham": "Tottenham Hotspur",
        "Spurs": "Tottenham Hotspur",
        "West Ham": "West Ham United",
        "Wolves": "Wolverhampton Wanderers",
        "Wolverhampton Wanderers": "Wolverhampton Wanderers",
        "Leicester": "Leicester City",
        "Leicester City": "Leicester City",
        "Leeds": "Leeds United",
        "Leeds United": "Leeds United",
        "Southampton": "Southampton",
    }
            
    # Build master club dictionary for string matching
    master_clubs_df = pd.read_csv('data/entity_resolution/master_club.csv')
    canon_to_id = {row['canonical_name']: row['master_club_id'] for _, row in master_clubs_df.iterrows()}
    
    new_clubs = []
    def resolve_club(name):
        import uuid, re
        if name == 'UNKNOWN' or not name: return 'UNKNOWN'
        
        name_clean = re.sub(r'\b(FC|AFC)\b', '', name, flags=re.IGNORECASE).strip()
        canonical = canonical_mapping.get(name_clean, name_clean)
        
        if canonical in canon_to_id:
            return canon_to_id[canonical]
            
        name_lower = canonical.lower()
        for cname, cid in canon_to_id.items():
            if cname.lower() == name_lower:
                canon_to_id[canonical] = cid
                return cid
                
        # create new club
        new_id = f"club_{str(uuid.uuid4())[:8]}"
        canon_to_id[canonical] = new_id
        new_clubs.append({"master_club_id": new_id, "canonical_name": canonical})
        return new_id

    # Load transfers_normalized
    norm_df = pd.read_csv('data/processed/transfers_normalized.csv')
    
    updated_count = 0
    for idx, row in norm_df.iterrows():
        tid = row['transfer_id']
        if tid in tid_map:
            from_club_str = tid_map[tid]['from_club']
            to_club_str = tid_map[tid]['to_club']
            
            from_id = resolve_club(from_club_str)
            to_id = resolve_club(to_club_str)
            
            if from_id != 'UNKNOWN': norm_df.at[idx, 'from_club_id'] = from_id
            if to_id != 'UNKNOWN': norm_df.at[idx, 'to_club_id'] = to_id
            updated_count += 1
            
    print(f"Updated {updated_count} transfers with clubs.")
    norm_df.to_csv('data/processed/transfers_normalized.csv', index=False)
    
    if new_clubs:
        print(f"Created {len(new_clubs)} new clubs. Appending to master_club.csv...")
        pd.DataFrame(new_clubs).to_csv('data/entity_resolution/master_club.csv', mode='a', header=False, index=False)

if __name__ == '__main__':
    fix_transfers()
