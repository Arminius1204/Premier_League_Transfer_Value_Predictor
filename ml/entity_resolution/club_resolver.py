import csv
import uuid
import re
from pathlib import Path

class ClubResolver:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.master_clubs = {}
        self.club_identity_map = []
        
        # Hardcoded canonical mapping for 2023/24 EPL to bootstrap
        self.canonical_mapping = {
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
            "Wolverhampton Wanderers": "Wolverhampton Wanderers"
        }

    def _normalize(self, name):
        if not name:
            return ""
        # Remove FC, AFC, etc.
        name = re.sub(r'\b(FC|AFC)\b', '', name, flags=re.IGNORECASE).strip()
        return name

    def resolve(self, parsed_data_sources):
        # Create master records from our canonical list
        canonical_to_id = {}
        for alias, canonical in self.canonical_mapping.items():
            if canonical not in canonical_to_id:
                master_id = f"club_{str(uuid.uuid4())[:8]}"
                canonical_to_id[canonical] = master_id
                self.master_clubs[master_id] = {
                    "master_club_id": master_id,
                    "canonical_name": canonical
                }
                
        for source_name, filepath in parsed_data_sources:
            if not Path(filepath).exists():
                continue
                
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    club_fields = []
                    if source_name == "fpl":
                        club_fields.append((row.get("source_club_id"), row.get("source_club_name")))
                    elif source_name == "football_data":
                        club_fields.append((row.get("source_home_team"), row.get("source_home_team")))
                        club_fields.append((row.get("source_away_team"), row.get("source_away_team")))
                        
                    for src_id, src_name in club_fields:
                        if not src_name:
                            continue
                            
                        norm_name = self._normalize(src_name)
                        canonical = self.canonical_mapping.get(norm_name, norm_name)
                        
                        # If unknown, create new master
                        if canonical not in canonical_to_id:
                            master_id = f"club_{str(uuid.uuid4())[:8]}"
                            canonical_to_id[canonical] = master_id
                            self.master_clubs[master_id] = {
                                "master_club_id": master_id,
                                "canonical_name": canonical
                            }
                            
                        master_id = canonical_to_id[canonical]
                        
                        # Add to identity map if not already present
                        mapping = {
                            "master_club_id": master_id,
                            "source": source_name,
                            "source_club_id": src_id or src_name,
                            "source_club_name": src_name
                        }
                        if mapping not in self.club_identity_map:
                            self.club_identity_map.append(mapping)

    def save(self, output_dir):
        out_dir = Path(output_dir)
        
        with open(out_dir / "master_club.csv", 'w', newline='', encoding='utf-8') as f:
            if self.master_clubs:
                writer = csv.DictWriter(f, fieldnames=["master_club_id", "canonical_name"])
                writer.writeheader()
                writer.writerows(self.master_clubs.values())
                
        with open(out_dir / "club_identity_map.csv", 'w', newline='', encoding='utf-8') as f:
            if self.club_identity_map:
                writer = csv.DictWriter(f, fieldnames=["master_club_id", "source", "source_club_id", "source_club_name"])
                writer.writeheader()
                writer.writerows(self.club_identity_map)
                
        return len(self.master_clubs), len(self.club_identity_map)
