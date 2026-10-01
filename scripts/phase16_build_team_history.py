import pandas as pd
import glob
from pathlib import Path

# FBRef name mappings for football-data.co.uk names
team_mapping = {
    # England
    "Man City": "Manchester City",
    "Man United": "Manchester Utd",
    "Newcastle": "Newcastle Utd",
    "Nott'm Forest": "Nott'ham Forest",
    "Sheffield Weds": "Sheffield Wed",
    "Sheffield Utd": "Sheffield Utd",
    "Luton": "Luton Town",
    "Wolves": "Wolverhampton",
    
    # Germany
    "Bayern Munich": "Bayern Munich",
    "Dortmund": "Dortmund",
    "Leverkusen": "Leverkusen",
    "RB Leipzig": "RB Leipzig",
    "Union Berlin": "Union Berlin",
    "Stuttgart": "Stuttgart",
    "Freiburg": "Freiburg",
    "Wolfsburg": "Wolfsburg",
    "Eintracht Frankfurt": "Eint Frankfurt",
    "M'gladbach": "M'Gladbach",
    "Werder Bremen": "Werder Bremen",
    "Mainz": "Mainz 05",
    "Hoffenheim": "Hoffenheim",
    "Bochum": "Bochum",
    "Augsburg": "Augsburg",
    "FC Koln": "Köln",
    "Schalke 04": "Schalke 04",
    "Hertha": "Hertha BSC",
    "Arminia": "Arminia",
    "Bielefeld": "Arminia",
    
    # Spain
    "Real Madrid": "Real Madrid",
    "Barcelona": "Barcelona",
    "Ath Madrid": "Atlético Madrid",
    "Girona": "Girona",
    "Ath Bilbao": "Athletic Club",
    "Sociedad": "Real Sociedad",
    "Betis": "Real Betis",
    "Villarreal": "Villarreal",
    "Valencia": "Valencia",
    "Sevilla": "Sevilla",
    
    # Italy
    "Inter": "Inter",
    "Milan": "Milan",
    "Juventus": "Juventus",
    "Roma": "Roma",
    "Napoli": "Napoli",
    "Lazio": "Lazio",
    "Atalanta": "Atalanta",
    "Fiorentina": "Fiorentina",
    
    # France
    "PSG": "Paris S-G",
    "Monaco": "Monaco",
    "Marseille": "Marseille",
    "Lille": "Lille",
    "Lens": "Lens",
    "Lyon": "Lyon",
    "Rennes": "Rennes"
}

def build_team_history():
    files = glob.glob('data/raw/football_data/*.csv')
    records = []
    
    for f in files:
        # filename format: lg_season.csv e.g. D1_2122.csv
        name = Path(f).stem
        parts = name.split('_')
        lg = parts[0]
        season_str = parts[1]
        
        # map 2122 to 2021_2022
        if len(season_str) == 4:
            s1 = int(season_str[:2])
            s2 = int(season_str[2:])
            s_full = f"20{s1}_20{s2}"
        else:
            s_full = season_str
            
        try:
            df = pd.read_csv(f, encoding='latin1')
            if df.empty or 'HomeTeam' not in df.columns:
                continue
            
            # Aggregate stats
            for team in set(df['HomeTeam'].dropna()).union(set(df['AwayTeam'].dropna())):
                home_matches = df[df['HomeTeam'] == team]
                away_matches = df[df['AwayTeam'] == team]
                
                # points
                home_pts = sum(home_matches['FTR'] == 'H') * 3 + sum(home_matches['FTR'] == 'D')
                away_pts = sum(away_matches['FTR'] == 'A') * 3 + sum(away_matches['FTR'] == 'D')
                pts = home_pts + away_pts
                
                # goals
                gf = home_matches['FTHG'].sum() + away_matches['FTAG'].sum()
                ga = home_matches['FTAG'].sum() + away_matches['FTHG'].sum()
                gd = gf - ga
                
                canonical_team = team_mapping.get(team, team)
                
                records.append({
                    'club': canonical_team,
                    'season_id': s_full,
                    'pts': pts,
                    'gd': gd
                })
        except Exception as e:
            print(f"Error parsing {f}: {e}")
            
    res = pd.DataFrame(records)
    res.to_csv('data/processed/team_history.csv', index=False)
    print(f"Built team_history.csv with {len(res)} records.")

if __name__ == "__main__":
    build_team_history()
