import csv
import json
import re
import math
import uuid
from pathlib import Path
from bs4 import BeautifulSoup
from difflib import SequenceMatcher

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROC_DIR = PROJECT_ROOT / "data" / "processed"
ER_DIR = PROJECT_ROOT / "data" / "entity_resolution"
DOCS_DIR = PROJECT_ROOT / "docs"

def safe_float(v):
    try:
        return float(v)
    except:
        return None

def fuzzy_score(s1, s2):
    return SequenceMatcher(None, s1.lower(), s2.lower()).ratio() * 100

def get_position_group(raw_pos):
    raw = raw_pos.lower()
    if 'goalkeeper' in raw: return 'GOALKEEPER'
    if 'back' in raw or 'defender' in raw: return 'DEFENDER'
    if 'midfield' in raw: return 'MIDFIELDER'
    if 'forward' in raw or 'winger' in raw or 'striker' in raw or 'attack' in raw: return 'FORWARD'
    return 'UNKNOWN'

def build_features():
    # 1. Load normalized transfers
    transfers = []
    with open(PROC_DIR / 'transfers_normalized.csv', 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row['target_eligible'] == 'TRUE':
                transfers.append(row)
                
    # 2. Extract demographics and selling club from TM raw files
    tm_enriched = {}
    for file in RAW_DIR.rglob("transfermarkt*.html"):
        season_id = file.name.split("_pl_")[1].replace(".html", "")
        with open(file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            for tr in soup.find_all("tr"):
                cols = tr.find_all("td")
                if len(cols) < 8: continue
                
                a = tr.find("a", href=re.compile(r'/profil/spieler/'))
                if not a: continue
                
                href = a.get("href", "")
                pid_match = re.search(r'/spieler/(\d+)', href)
                if not pid_match: continue
                
                source_pid = pid_match.group(1)
                
                # Demographics
                age = cols[1].text.strip()
                nat_imgs = cols[2].find_all('img')
                nationality = nat_imgs[0].get('alt', 'Unknown') if nat_imgs else 'Unknown'
                position = cols[3].text.strip()
                
                # Selling club
                # Transfermarkt lists left club in col 5 or 7 depending on in/out view. 
                # Let's check col 7 (Left Club Name typically if viewing a team's arrivals, but if viewing league transfers it might be different).
                # Actually, in league transfers: col 6 is Left Club badge, 7 is Left club name.
                selling_club = cols[7].text.strip()
                # Clean weird characters
                selling_club = re.sub(r'[^\w\s-]', '', selling_club).strip()
                
                key = f"{source_pid}_{season_id}"
                tm_enriched[key] = {
                    "age": age,
                    "nationality": nationality,
                    "position": position,
                    "selling_club_name": selling_club
                }

    # Load master clubs for matching
    master_clubs = []
    with open(PROC_DIR / 'clubs.csv', 'r', encoding='utf-8') as f:
        master_clubs = list(csv.DictReader(f))
        
    def match_club(name):
        if not name or name == "Unknown" or name == "Without Club" or name == "Retired":
            return None
        best = None
        best_score = 0
        for mc in master_clubs:
            score = fuzzy_score(name, mc["canonical_name"])
            if score > best_score:
                best_score = score
                best = mc["master_club_id"]
        return best if best_score > 60 else None

    # Load TM -> Master Player map to link source_pid to transfer record
    tm_pid_to_master = {}
    master_to_tmpid = {}
    with open(ER_DIR / 'player_identity_map.csv', 'r', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r['source'] == 'transfermarkt':
                tm_pid_to_master[r['source_player_id']] = r['master_player_id']
                master_to_tmpid[r['master_player_id']] = r['source_player_id']

    # Load transfer performance links
    links = {}
    with open(PROC_DIR / 'transfer_performance_links.csv', 'r', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r['temporal_status'] == 'VALID':
                links[r['transfer_id']] = r['latest_valid_season']
                
    # Load player seasons (FPL)
    player_seasons = {}
    with open(PROC_DIR / 'player_seasons.csv', 'r', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            key = f"{r['master_player_id']}_{r['season_id']}"
            player_seasons[key] = r

    # Load club context (T-1)
    club_context = {}
    with open(PROC_DIR / 'club_season_context.csv', 'r', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            key = f"{r['club_id']}_{r['season_id']}"
            club_context[key] = r

    # Build feature rows
    feature_rows = []
    
    for t in transfers:
        tid = t['transfer_id']
        master_pid = t['master_player_id']
        t_season = t['season_id']
        
        # 1. Target
        fee_gbp = safe_float(t['fee_gbp'])
        if fee_gbp is None or fee_gbp <= 0:
            continue
            
        fee_log = math.log1p(fee_gbp)
        
        # 2. Demographics (TM)
        tm_pid = master_to_tmpid.get(master_pid)
        demographics = tm_enriched.get(f"{tm_pid}_{t_season}", {})
        
        age = safe_float(demographics.get("age"))
        age_sq = age * age if age else ""
        
        raw_pos = demographics.get("position", "Unknown")
        norm_pos = get_position_group(raw_pos)
        nationality = demographics.get("nationality", "Unknown")
        
        # 3. Club Context (Selling Club)
        selling_club_name = demographics.get("selling_club_name", "Unknown")
        selling_club_id = match_club(selling_club_name)
        
        prev_season = links.get(tid)
        cc = {}
        if selling_club_id and prev_season:
            cc = club_context.get(f"{selling_club_id}_{prev_season}", {})
            
        prev_pts = cc.get("points", "")
        prev_gf = cc.get("gf", "")
        prev_ga = cc.get("ga", "")
        prev_gd = cc.get("gd", "")
        prev_matches = safe_float(cc.get("matches"))
        
        ppm = round(safe_float(prev_pts) / prev_matches, 3) if prev_matches and prev_pts else ""
        
        # 4. Player Performance (FPL T-1)
        perf = {}
        if prev_season:
            perf = player_seasons.get(f"{master_pid}_{prev_season}", {})
            
        mins = safe_float(perf.get("minutes"))
        goals = safe_float(perf.get("goals"))
        assists = safe_float(perf.get("assists"))
        xg = safe_float(perf.get("xG"))
        xa = safe_float(perf.get("xA"))
        
        low_minutes = "1" if (mins is not None and mins < 450) else "0"
        
        g_90 = round((goals / mins) * 90, 3) if (mins and goals is not None and mins > 0) else ""
        a_90 = round((assists / mins) * 90, 3) if (mins and assists is not None and mins > 0) else ""
        xg_90 = round((xg / mins) * 90, 3) if (mins and xg is not None and mins > 0) else ""
        
        row = {
            "transfer_id": tid,
            "master_player_id": master_pid,
            "season_id": t_season,
            "transfer_date": t['transfer_date'],
            "fee_gbp": fee_gbp,
            "log_fee_gbp": round(fee_log, 4),
            
            # Demographics
            "age_at_transfer": age if age else "",
            "age_squared": round(age_sq, 2) if age_sq else "",
            "position": norm_pos,
            "position_raw": raw_pos,
            "nationality": nationality,
            
            # Club Context
            "selling_club_id": selling_club_id if selling_club_id else "UNKNOWN",
            "prev_season_points": prev_pts,
            "prev_season_points_per_match": ppm,
            "prev_season_gd": prev_gd,
            
            # Player Performance
            "prev_season_minutes": mins if mins is not None else "",
            "low_minutes_flag": low_minutes if mins is not None else "UNKNOWN",
            "prev_season_goals": goals if goals is not None else "",
            "prev_season_goals_per90": g_90,
            "prev_season_xg_per90": xg_90
        }
        feature_rows.append(row)
        
    with open(PROC_DIR / 'transfer_features_candidate.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=feature_rows[0].keys())
        writer.writeheader()
        writer.writerows(feature_rows)
        
    print(f"Generated candidate dataset with {len(feature_rows)} eligible records.")

    # 5. Coverage Matrix
    coverage = {
        "age_at_transfer": {"src": "Transfermarkt", "valid": "VALID", "status": "CORE"},
        "position": {"src": "Transfermarkt", "valid": "VALID", "status": "CORE"},
        "nationality": {"src": "Transfermarkt", "valid": "VALID", "status": "CORE"},
        "prev_season_points": {"src": "football-data", "valid": "VALID", "status": "ENRICHED"},
        "prev_season_goals_per90": {"src": "FPL", "valid": "VALID", "status": "ENRICHED"}
    }
    
    cov_rows = []
    for f, v in coverage.items():
        # Count non-empty across seasons
        s_counts = {"2021_2022": [0,0], "2022_2023": [0,0], "2023_2024": [0,0]} # [present, total]
        for row in feature_rows:
            sid = row['season_id']
            if sid == '2023': sid = '2023_2024' # Merge 2023 and 2023_2024
            if sid in s_counts:
                s_counts[sid][1] += 1
                if row[f] != "": s_counts[sid][0] += 1
                
        cov_rows.append({
            "feature": f,
            "2021_2022": f"{s_counts['2021_2022'][0]}/{s_counts['2021_2022'][1]}",
            "2022_2023": f"{s_counts['2022_2023'][0]}/{s_counts['2022_2023'][1]}",
            "2023_2024": f"{s_counts['2023_2024'][0]}/{s_counts['2023_2024'][1]}",
            "overall_coverage": f"{sum(s[0] for s in s_counts.values())}/{sum(s[1] for s in s_counts.values())}",
            "source": v["src"],
            "temporal_validity": v["valid"],
            "status": v["status"]
        })
        
    with open(PROC_DIR / 'feature_coverage_matrix.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=cov_rows[0].keys())
        writer.writeheader()
        writer.writerows(cov_rows)
        
    print("Generated feature_coverage_matrix.csv")
    
if __name__ == "__main__":
    build_features()
