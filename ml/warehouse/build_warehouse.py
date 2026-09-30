import csv
import json
import re
from pathlib import Path
from datetime import datetime

# Setup Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PARSED_DIR = PROJECT_ROOT / "data" / "parsed"
ER_DIR = PROJECT_ROOT / "data" / "entity_resolution"
PROC_DIR = PROJECT_ROOT / "data" / "processed"
DOCS_DIR = PROJECT_ROOT / "docs"

def safe_float(val):
    try:
        return float(val)
    except:
        return 0.0

def build_audit():
    # Helper to count lines in csv safely
    def count_csv(path):
        if not path.exists(): return 0
        with open(path, 'r', encoding='utf-8') as f:
            return sum(1 for line in f) - 1 # exclude header
            
    raw_files = list(RAW_DIR.rglob("*.*"))
    parsed_files = list(PARSED_DIR.rglob("*.csv"))
    
    audit_md = f"# Phase 5 Data Audit\n\nGenerated: {datetime.utcnow().isoformat()}\n\n"
    audit_md += f"## 1. Raw Files\n- Total Raw Files (incl metadata): {len(raw_files)}\n\n"
    audit_md += f"## 2. Parsed Files\n- Total Parsed Files: {len(parsed_files)}\n"
    
    for pf in parsed_files:
        audit_md += f"  - `{pf.name}`: {count_csv(pf)} rows\n"
        
    audit_md += f"\n## 3. Entity Resolution\n"
    audit_md += f"- Master Players: {count_csv(ER_DIR / 'master_player.csv')}\n"
    audit_md += f"- Player Mappings: {count_csv(ER_DIR / 'player_identity_map.csv')}\n"
    audit_md += f"- Master Clubs: {count_csv(ER_DIR / 'master_club.csv')}\n"
    audit_md += f"- Club Mappings: {count_csv(ER_DIR / 'club_identity_map.csv')}\n"
    audit_md += f"- Review Queue: {count_csv(ER_DIR / 'review_queue.csv')}\n"
    
    with open(DOCS_DIR / "phase5_data_audit.md", 'w', encoding='utf-8') as f:
        f.write(audit_md)
    print("Generated phase5_data_audit.md")

def build_dimensions():
    # 1. Seasons
    seasons = []
    with open(ER_DIR / "master_season.csv", 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            seasons.append(row)
    with open(PROC_DIR / "seasons.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=seasons[0].keys())
        writer.writeheader()
        writer.writerows(seasons)
        
    # 2. Clubs
    clubs = []
    with open(ER_DIR / "master_club.csv", 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            row["country"] = "England"
            row["league"] = "Premier League"
            clubs.append(row)
    with open(PROC_DIR / "clubs.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["master_club_id", "canonical_name", "country", "league"])
        writer.writeheader()
        writer.writerows(clubs)
        
    # 3. Players
    players = []
    with open(ER_DIR / "master_player.csv", 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            players.append(row)
    with open(PROC_DIR / "players.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=players[0].keys())
        writer.writeheader()
        writer.writerows(players)
    
    print("Generated Dimensional Tables (seasons, clubs, players)")

def build_transfers():
    # Player Identity Map for lookups
    player_map = {}
    with open(ER_DIR / "player_identity_map.csv", 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row["source"] == "transfermarkt":
                player_map[row["source_player_id"]] = row["master_player_id"]
                
    transfers = []
    
    for tm_file in PARSED_DIR.rglob("transfermarkt_parsed_*.csv"):
        with open(tm_file, 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                source_pid = row["source_player_id"]
                master_pid = player_map.get(source_pid)
                
                if not master_pid:
                    continue # Skip if no master identity
                    
                fee_status = row["fee_status"]
                raw_fee = row["raw_fee_string"]
                
                fee_numeric = None
                fee_currency = None
                
                if fee_status == "DISCLOSED":
                    # Fix encoding errors and missed heuristics
                    if "end of loan" in raw_fee.lower() or "leihe" in raw_fee.lower() or "loan transfer" in raw_fee.lower():
                        fee_status = "LOAN"
                    elif "free transfer" in raw_fee.lower() or "ablösefrei" in raw_fee.lower():
                        fee_status = "FREE"
                    elif raw_fee.strip() == "-" or "?" in raw_fee:
                        fee_status = "UNKNOWN"
                    else:
                        # Parse currency
                        if '€' in raw_fee or '' in raw_fee: fee_currency = 'EUR'
                        elif '£' in raw_fee: fee_currency = 'GBP'
                        else: fee_currency = 'UNKNOWN'
                        
                        # Parse numeric
                        num_match = re.search(r'[\d,\.]+', raw_fee)
                        if num_match:
                            val = float(num_match.group(0).replace(',', ''))
                            if 'm' in raw_fee.lower(): val *= 1000000
                            elif 'k' in raw_fee.lower(): val *= 1000
                            fee_numeric = val
                
                if fee_status in ("FREE", "LOAN"):
                    fee_numeric = 0.0
                
                target_eligible = "TRUE" if (fee_status == "DISCLOSED" and fee_numeric is not None) else "FALSE"
                if fee_status == "DISCLOSED" and fee_numeric is None:
                    exclusion_reason = "UNPARSEABLE FEE VALUE"
                elif fee_status != "DISCLOSED":
                    exclusion_reason = f"FEE IS {fee_status}"
                else:
                    exclusion_reason = ""
                
                # We do not have exact date from our simple parser, using a proxy
                season_id = row["season_id"]
                start_year = season_id.split('_')[0] if '_' in season_id else season_id
                proxy_date = f"{start_year}-07-01"
                
                # FX Logic
                # Using known July 1st mid-market rates for the respective years.
                fx_rates = {
                    "2018": 0.89,
                    "2019": 0.90,
                    "2020": 0.90,
                    "2021": 0.858,
                    "2022": 0.859,
                    "2023": 0.859
                }
                
                fee_gbp = ""
                if fee_numeric is not None and fee_status == "DISCLOSED":
                    if fee_currency == "GBP":
                        fee_gbp = fee_numeric
                    elif fee_currency == "EUR":
                        rate = fx_rates.get(start_year, 0.859) # fallback to 0.859
                        fee_gbp = round(fee_numeric * rate, 2)
                        
                if fee_status in ("FREE", "LOAN"):
                    fee_gbp = 0.0
                
                transfers.append({
                    "transfer_id": row["transfer_id"],
                    "master_player_id": master_pid,
                    "season_id": season_id,
                    "transfer_date": proxy_date,
                    "from_club_id": "UNKNOWN", # Need detailed TM parsing for clubs
                    "to_club_id": "UNKNOWN",
                    "fee_status": fee_status,
                    "fee_numeric": fee_numeric if fee_numeric is not None else "",
                    "fee_currency": fee_currency if fee_currency else "",
                    "fee_gbp": fee_gbp if fee_gbp != "" else "",
                    "target_eligible": target_eligible,
                    "exclusion_reason": exclusion_reason
                })
                
    with open(PROC_DIR / "transfers_normalized.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=transfers[0].keys())
        writer.writeheader()
        writer.writerows(transfers)
        
    print(f"Generated transfers_normalized.csv with {len(transfers)} records.")

def build_club_context():
    club_map = {}
    with open(ER_DIR / "club_identity_map.csv", 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row["source"] == "football_data":
                club_map[row["source_club_name"]] = row["master_club_id"]
                
    matches = []
    context = {}
    
    for fd_file in PARSED_DIR.rglob("football_data_parsed_*.csv"):
        # filter out '2324' if '2023_2024' exists
        if len(fd_file.name) < 30: continue
            
        with open(fd_file, 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                season = row["season_id"]
                home_team = club_map.get(row["source_home_team"])
                away_team = club_map.get(row["source_away_team"])
                
                if not home_team or not away_team:
                    continue
                    
                hg = safe_float(row["home_goals"])
                ag = safe_float(row["away_goals"])
                
                matches.append({
                    "match_id": row["source_match_id"],
                    "season_id": season,
                    "date": row["match_date"],
                    "home_club_id": home_team,
                    "away_club_id": away_team,
                    "home_goals": hg,
                    "away_goals": ag
                })
                
                # Aggregate Home
                home_key = f"{home_team}_{season}"
                if home_key not in context:
                    context[home_key] = {"club_id": home_team, "season_id": season, "matches": 0, "wins": 0, "draws": 0, "losses": 0, "points": 0, "gf": 0, "ga": 0}
                
                context[home_key]["matches"] += 1
                context[home_key]["gf"] += hg
                context[home_key]["ga"] += ag
                if hg > ag: 
                    context[home_key]["wins"] += 1
                    context[home_key]["points"] += 3
                elif hg == ag:
                    context[home_key]["draws"] += 1
                    context[home_key]["points"] += 1
                else:
                    context[home_key]["losses"] += 1
                    
                # Aggregate Away
                away_key = f"{away_team}_{season}"
                if away_key not in context:
                    context[away_key] = {"club_id": away_team, "season_id": season, "matches": 0, "wins": 0, "draws": 0, "losses": 0, "points": 0, "gf": 0, "ga": 0}
                
                context[away_key]["matches"] += 1
                context[away_key]["gf"] += ag
                context[away_key]["ga"] += hg
                if ag > hg: 
                    context[away_key]["wins"] += 1
                    context[away_key]["points"] += 3
                elif ag == hg:
                    context[away_key]["draws"] += 1
                    context[away_key]["points"] += 1
                else:
                    context[away_key]["losses"] += 1

    if matches:
        with open(PROC_DIR / "matches.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=matches[0].keys())
            writer.writeheader()
            writer.writerows(matches)
            
    ctx_list = []
    for k, v in context.items():
        v["gd"] = v["gf"] - v["ga"]
        ctx_list.append(v)
        
    if ctx_list:
        with open(PROC_DIR / "club_season_context.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=ctx_list[0].keys())
            writer.writeheader()
            writer.writerows(ctx_list)
            
    print("Generated matches.csv and club_season_context.csv")

def build_player_seasons():
    player_map = {}
    club_map = {}
    with open(ER_DIR / "player_identity_map.csv", 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row["source"] == "fpl": player_map[row["source_player_id"]] = row["master_player_id"]
    with open(ER_DIR / "club_identity_map.csv", 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row["source"] == "fpl": club_map[row["source_club_id"]] = row["master_club_id"]

    seasons = []
    
    for season in ["2018_2019", "2019_2020", "2020_2021", "2021_2022", "2022_2023", "2023_2024"]:
        fpl_file = PARSED_DIR / "fpl_historical" / f"fpl_historical_parsed_{season}.csv"
        if not fpl_file.exists(): continue
        
        with open(fpl_file, 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                master_pid = player_map.get(row["source_player_id"])
                
                # We don't have source_club_id directly in historical vaastav players output without mapping,
                # but we will just pass UNKNOWN and allow club context to handle it, 
                # or if there's a club id we can map it. For now, player_seasons cares about stats.
                master_cid = "UNKNOWN" 
                
                if master_pid:
                    seasons.append({
                        "master_player_id": master_pid,
                        "season_id": row["season_id"],
                        "master_club_id": master_cid,
                        "minutes": row.get("minutes", 0),
                        "goals": row.get("goals_scored", 0),
                        "assists": row.get("assists", 0),
                        "bps": row.get("bps", 0)
                    })
                
    if seasons:
        with open(PROC_DIR / "player_seasons.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=seasons[0].keys())
            writer.writeheader()
            writer.writerows(seasons)
            
        with open(PROC_DIR / "player_season_clubs.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["master_player_id", "season_id", "master_club_id"])
            writer.writeheader()
            for s in seasons:
                writer.writerow({"master_player_id": s["master_player_id"], "season_id": s["season_id"], "master_club_id": s["master_club_id"]})
                
    print(f"Generated player_seasons.csv ({len(seasons)} records)")

def build_transfer_links():
    links = []
    
    # Simple logic: previous season string logic
    season_shift = {
        "2023_2024": "2022_2023",
        "2022_2023": "2021_2022",
        "2021_2022": "2020_2021",
        "2020_2021": "2019_2020",
        "2019_2020": "2018_2019",
        "2018_2019": "2017_2018"
    }
    
    with open(PROC_DIR / "transfers_normalized.csv", 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row["target_eligible"] == "TRUE":
                trans_season = row["season_id"]
                valid_season = season_shift.get(trans_season, "UNKNOWN")
                links.append({
                    "transfer_id": row["transfer_id"],
                    "master_player_id": row["master_player_id"],
                    "transfer_date": row["transfer_date"],
                    "latest_valid_season": valid_season,
                    "temporal_status": "VALID" if valid_season != "UNKNOWN" else "UNKNOWN"
                })
                
    if links:
        with open(PROC_DIR / "transfer_performance_links.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=links[0].keys())
            writer.writeheader()
            writer.writerows(links)
    print("Generated transfer_performance_links.csv")

def build_temporal_validity():
    fields = [
        {"feature_name": "previous_season_goals", "source": "FPL/Understat", "observation_period": "T-1 Season", "temporal_status": "VALID", "leakage_risk": "LOW", "notes": "Safe for summer transfers"},
        {"feature_name": "current_season_goals", "source": "FPL", "observation_period": "T Season", "temporal_status": "INVALID", "leakage_risk": "HIGH", "notes": "Cannot use end of season stats to predict transfer at start of season"},
        {"feature_name": "market_value", "source": "Transfermarkt", "observation_period": "Unknown/Retroactive", "temporal_status": "INVALID", "leakage_risk": "HIGH", "notes": "Requires strict timestamp alignment to be safe"}
    ]
    with open(PROC_DIR / "feature_temporal_validity.csv", 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields[0].keys())
        writer.writeheader()
        writer.writerows(fields)
    print("Generated feature_temporal_validity.csv")

if __name__ == "__main__":
    build_audit()
    build_dimensions()
    build_transfers()
    build_club_context()
    build_player_seasons()
    build_transfer_links()
    build_temporal_validity()
    print("Warehouse Build Complete!")
