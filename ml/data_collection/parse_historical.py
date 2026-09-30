import os
import csv
import json
from pathlib import Path
from bs4 import BeautifulSoup
import uuid

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PARSED_DIR = PROJECT_ROOT / "data" / "parsed"

SEASONS = ["2018_2019", "2019_2020", "2020_2021", "2021_2022", "2022_2023", "2023_2024"]

def parse_football_data():
    out_dir = PARSED_DIR / "football_data"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    for season in SEASONS:
        in_file = RAW_DIR / "football_data" / f"E0_{season}.csv"
        if not in_file.exists(): continue
        
        parsed = []
        with open(in_file, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if "HomeTeam" not in row or not row["HomeTeam"]: continue
                parsed.append({
                    "source_match_id": f"fd_{season}_{row['HomeTeam']}_{row['AwayTeam']}",
                    "season_id": season,
                    "match_date": row.get("Date", ""),
                    "source_home_team": row["HomeTeam"],
                    "source_away_team": row["AwayTeam"],
                    "home_goals": row.get("FTHG", 0),
                    "away_goals": row.get("FTAG", 0)
                })
        
        if parsed:
            with open(out_dir / f"football_data_parsed_{season}.csv", 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=parsed[0].keys())
                writer.writeheader()
                writer.writerows(parsed)
            print(f"Parsed {len(parsed)} matches for {season}")

def parse_transfermarkt():
    out_dir = PARSED_DIR / "transfermarkt"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    for season in SEASONS:
        # Transfermarkt files are sometimes named pl_2023 instead of pl_2023_2024
        # Let's map it safely.
        tm_season_str = season
        in_file = RAW_DIR / "transfermarkt" / f"transfermarkt_pl_{tm_season_str}.html"
        if not in_file.exists():
            in_file = RAW_DIR / "transfermarkt" / f"transfermarkt_pl_{season.split('_')[0]}.html"
            
        if not in_file.exists(): 
            print(f"Missing TM for {season}")
            continue
            
        with open(in_file, 'r', encoding='utf-8') as f:
            html = f.read()
            
        soup = BeautifulSoup(html, 'html.parser')
        boxes = soup.find_all("div", class_="box")
        
        parsed = []
        for box in boxes:
            header = box.find("h2")
            if not header: continue
            
            club_link = header.find("a")
            if not club_link: continue
            
            buying_club_id = club_link.get("href").split("/")[4] if len(club_link.get("href").split("/")) > 4 else "unknown"
            buying_club_name = club_link.text.strip()
            
            tables = box.find_all("table")
            if not tables: continue
            
            # In transfers list, usually In is first table, Out is second
            table_in = tables[0]
            rows = table_in.find_all("tr")
            for r in rows:
                cols = r.find_all("td")
                if len(cols) < 8: continue
                
                player_link = cols[0].find("a", class_="hide-for-small")
                if not player_link: continue
                
                pid = player_link.get("href").split("/")[-1]
                pname = player_link.text.strip()
                
                fee_col = cols[8].text.strip() if len(cols) > 8 else cols[7].text.strip()
                
                parsed.append({
                    "transfer_id": f"tm_{pid}_{season}",
                    "season_id": season,
                    "source_player_id": pid,
                    "source_player_name": pname,
                    "source_buying_club_id": buying_club_id,
                    "source_buying_club_name": buying_club_name,
                    "raw_fee_text": fee_col
                })
                
        if parsed:
            with open(out_dir / f"transfermarkt_parsed_{season}.csv", 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=parsed[0].keys())
                writer.writeheader()
                writer.writerows(parsed)
            print(f"Parsed {len(parsed)} transfers for {season}")

def parse_fpl_historical():
    out_dir = PARSED_DIR / "fpl_historical"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    for season in SEASONS:
        in_file = RAW_DIR / "fpl_historical" / f"fpl_players_{season}.csv"
        if not in_file.exists(): continue
        
        parsed = []
        with open(in_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # FPL historical uses 'first_name' and 'second_name'
                # Element is the player ID if present, otherwise we make one from name
                pid = row.get("element", row.get("id", f"{row.get('first_name')}_{row.get('second_name')}"))
                fname = row.get("first_name", "")
                lname = row.get("second_name", "")
                pname = f"{fname} {lname}".strip()
                
                parsed.append({
                    "source_player_id": pid,
                    "season_id": season,
                    "source_player_name": pname,
                    "minutes": row.get("minutes", 0),
                    "goals_scored": row.get("goals_scored", 0),
                    "assists": row.get("assists", 0),
                    "bps": row.get("bps", 0),
                    "influence": row.get("influence", 0.0),
                    "creativity": row.get("creativity", 0.0),
                    "threat": row.get("threat", 0.0)
                })
                
        if parsed:
            with open(out_dir / f"fpl_historical_parsed_{season}.csv", 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=parsed[0].keys())
                writer.writeheader()
                writer.writerows(parsed)
            print(f"Parsed {len(parsed)} FPL players for {season}")

if __name__ == "__main__":
    parse_football_data()
    parse_transfermarkt()
    parse_fpl_historical()
