import csv
import uuid
import re
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher

class PlayerResolver:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.master_players = {}
        self.player_identity_map = []
        self.review_queue = []
        
    def _normalize(self, name):
        if not name:
            return ""
        # Lowercase, remove accents (simplistic fallback to ascii if unicodedata not available, but lower+strip is basic)
        name = name.lower()
        # Remove common punctuation
        name = re.sub(r"[^\w\s]", "", name)
        # Remove extra spaces
        name = " ".join(name.split())
        return name

    def _fuzzy_score(self, a, b):
        return SequenceMatcher(None, a, b).ratio() * 100

    def resolve(self, parsed_data_sources, master_clubs):
        # parsed_data_sources is a list of (source_name, filepath)
        
        # Pass 1: Bootstrap Master Player table using the richest source (FPL in this case)
        # In a real scenario, Transfermarkt would be the base because it has Date of Birth.
        # FPL doesn't have DOB, so we create a master record with what we have.
        
        # Deduplication tracker for Pass 1
        fpl_seen = {}
        
        for source_name, filepath in parsed_data_sources:
            if not Path(filepath).exists() or source_name != "fpl":
                continue
                
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    src_id = row.get("source_player_id")
                    src_name = row.get("source_player_name")
                    src_club = row.get("source_club_name")
                    
                    norm_name = self._normalize(src_name)
                    
                    # Deduplicate by source_player_id or normalized name
                    dedup_key = src_id if src_id else norm_name
                    
                    if dedup_key in fpl_seen:
                        master_id = fpl_seen[dedup_key]
                    else:
                        master_id = f"plr_{str(uuid.uuid4())[:8]}"
                        fpl_seen[dedup_key] = master_id
                        
                        # Create Master Record only once
                        self.master_players[master_id] = {
                            "master_player_id": master_id,
                            "canonical_name": norm_name,
                            "date_of_birth": "", # FPL lacks DOB
                            "canonical_position": "", 
                            "nationality": "",
                            "height": "",
                            "preferred_foot": "",
                            "created_at": datetime.utcnow().isoformat() + "Z"
                        }
                    
                    # Add Identity Map for this specific season occurrence
                    self.player_identity_map.append({
                        "master_player_id": master_id,
                        "source": source_name,
                        "source_player_id": src_id,
                        "source_player_name": src_name,
                        "source_club_id": row.get("source_club_id"),
                        "source_club_name": src_club,
                        "season_id": row.get("season_id"),
                        "match_confidence": 100.0,
                        "match_method": "EXACT_SOURCE_ID",
                        "review_status": "APPROVED"
                    })

        # Pass 2: Match other sources against Master table
        # We don't have other player datasets successfully parsed yet (Understat failed, FBref blocked).
        # But we will write the logic for future sources.
        
        for source_name, filepath in parsed_data_sources:
            if not Path(filepath).exists() or source_name == "fpl":
                continue
                
            if source_name == "transfermarkt":
                print(f"Processing transfermarkt file: {filepath}")
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        src_id = row.get("source_player_id")
                        src_name = row.get("source_player_name")
                        norm_name = self._normalize(src_name)
                        
                        best_match = None
                        best_score = 0
                        
                        # Compare against master players
                        for master_id, master_data in self.master_players.items():
                            master_name = master_data["canonical_name"]
                            
                            if norm_name == master_name:
                                best_score = 100.0
                                best_match = master_id
                                break
                            
                            # Only compute fuzzy if starting characters match or lengths are similar
                            if abs(len(master_name) - len(norm_name)) <= 4 and (master_name[:2] == norm_name[:2] or master_name[-2:] == norm_name[-2:]):
                                score = self._fuzzy_score(norm_name, master_name)
                                if score > best_score:
                                    best_score = score
                                    best_match = master_id
                                
                        if best_score == 100.0:
                            match_method = "EXACT_NAME"
                            status = "APPROVED"
                        elif best_score > 90.0:
                            match_method = "FUZZY_HIGH"
                            status = "APPROVED"
                        elif best_score > 80.0:
                            match_method = "FUZZY_MEDIUM"
                            status = "REVIEW_REQUIRED"
                        else:
                            # Create new master player if not found
                            best_match = f"plr_{str(uuid.uuid4())[:8]}"
                            self.master_players[best_match] = {
                                "master_player_id": best_match,
                                "canonical_name": norm_name,
                                "date_of_birth": "", 
                                "canonical_position": "", 
                                "nationality": "",
                                "height": "",
                                "preferred_foot": "",
                                "created_at": datetime.utcnow().isoformat() + "Z"
                            }
                            match_method = "NO_MATCH_CREATED_NEW"
                            status = "APPROVED"
                            best_score = 100.0
                            
                        # Add Identity Map
                        mapping = {
                            "master_player_id": best_match,
                            "source": source_name,
                            "source_player_id": src_id,
                            "source_player_name": src_name,
                            "source_club_id": "",
                            "source_club_name": "",
                            "season_id": row.get("season_id"),
                            "match_confidence": round(best_score, 2),
                            "match_method": match_method,
                            "review_status": status
                        }
                        if mapping not in self.player_identity_map:
                            self.player_identity_map.append(mapping)
                            
                        if status == "REVIEW_REQUIRED":
                            self.review_queue.append({
                                "source_player_name": src_name,
                                "candidate_master_player": best_match,
                                "name_score": round(best_score, 2),
                                "club": "",
                                "position": "",
                                "season": row.get("season_id"),
                                "confidence": "MEDIUM",
                                "reason": "Fuzzy score between 80 and 90"
                            })

    def save(self, output_dir):
        out_dir = Path(output_dir)
        
        # Save Master Players
        with open(out_dir / "master_player.csv", 'w', newline='', encoding='utf-8') as f:
            if self.master_players:
                fieldnames = ["master_player_id", "canonical_name", "date_of_birth", "canonical_position", 
                              "nationality", "height", "preferred_foot", "created_at"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.master_players.values())
                
        # Save Identity Map
        with open(out_dir / "player_identity_map.csv", 'w', newline='', encoding='utf-8') as f:
            if self.player_identity_map:
                fieldnames = ["master_player_id", "source", "source_player_id", "source_player_name", 
                              "source_club_id", "source_club_name", "season_id", "match_confidence", 
                              "match_method", "review_status"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.player_identity_map)
                
        # Save Review Queue
        with open(out_dir / "review_queue.csv", 'w', newline='', encoding='utf-8') as f:
            fieldnames = ["source_player_name", "candidate_master_player", "name_score", 
                          "club", "position", "season", "confidence", "reason"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            if self.review_queue:
                writer.writerows(self.review_queue)
                
        return len(self.master_players), len(self.player_identity_map), len(self.review_queue)
