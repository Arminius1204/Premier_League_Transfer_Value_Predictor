import json
import csv
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from pathlib import Path
from pathlib import Path
from ml.data_parsing.fpl_parser import FPLParser
from ml.data_parsing.football_data_parser import FootballDataParser
from ml.data_parsing.understat_parser import UnderstatParser
from ml.data_parsing.transfermarkt_parser import TransfermarktParser

def profile_parsed_files():
    parsed_dir = Path(__file__).resolve().parent.parent.parent / "data" / "parsed"
    profile_data = []
    
    total_records = 0
    total_files = 0
    
    for source_dir in parsed_dir.iterdir():
        if source_dir.is_dir():
            for csv_file in source_dir.glob("*.csv"):
                total_files += 1
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = list(csv.DictReader(f))
                    
                    if not reader:
                        continue
                        
                    row_count = len(reader)
                    total_records += row_count
                    columns = list(reader[0].keys())
                    
                    unique_players = set()
                    unique_clubs = set()
                    
                    for row in reader:
                        if "source_player_id" in row:
                            unique_players.add(row["source_player_id"])
                        elif "source_player_name" in row:
                            unique_players.add(row["source_player_name"])
                            
                        if "source_club_id" in row:
                            unique_clubs.add(row["source_club_id"])
                        elif "source_club_name" in row:
                            unique_clubs.add(row["source_club_name"])
                        elif "source_home_team" in row:
                            unique_clubs.add(row["source_home_team"])
                            unique_clubs.add(row["source_away_team"])
                            
                    profile = {
                        "source": source_dir.name,
                        "file_name": csv_file.name,
                        "row_count": row_count,
                        "column_count": len(columns),
                        "columns": columns,
                        "unique_players": len(unique_players) if unique_players else 0,
                        "unique_clubs": len(unique_clubs) if unique_clubs else 0
                    }
                    profile_data.append(profile)
                    
    with open(parsed_dir / "parsing_profile.json", 'w', encoding='utf-8') as f:
        json.dump(profile_data, f, indent=2)
        
    return profile_data, total_files, total_records

if __name__ == "__main__":
    print("Running FPL Parser...")
    fpl = FPLParser().parse()
    print("Running Football-Data Parser...")
    fd = FootballDataParser().parse()
    print("Running Understat Parser...")
    us = UnderstatParser().parse()
    print("Running Transfermarkt Parser...")
    tm = TransfermarktParser().parse()
    
    profiles, total_files, total_records = profile_parsed_files()
    
    print("\nPARSING SUMMARY:")
    for p in profiles:
        print(f"{p['source']} | {p['file_name']} -> {p['row_count']} rows, {p['unique_players']} players, {p['unique_clubs']} clubs")
    
    print(f"\nTotal Parsed Files: {total_files}")
    print(f"Total Parsed Records: {total_records}")
