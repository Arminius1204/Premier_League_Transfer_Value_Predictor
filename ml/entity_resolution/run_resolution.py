import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from pathlib import Path
from ml.entity_resolution.club_resolver import ClubResolver
from ml.entity_resolution.season_resolver import SeasonResolver
from ml.entity_resolution.player_resolver import PlayerResolver

def run():
    print("Starting Master Entity Resolution...\n")
    
    project_root = Path(__file__).resolve().parent.parent.parent
    data_dir = project_root / "data" / "parsed"
    out_dir = project_root / "data" / "entity_resolution"
    
    parsed_sources = []
    
    # Dynamically find all parsed files
    for f in (data_dir / "fpl_historical").rglob("*.csv"):
        parsed_sources.append(("fpl", f))
        
    for f in (data_dir / "football_data").rglob("*.csv"):
        parsed_sources.append(("football_data", f))
        
    for f in (data_dir / "transfermarkt").rglob("*.csv"):
        parsed_sources.append(("transfermarkt", f))
        
    print(f"Discovered {len(parsed_sources)} parsed dataset files for resolution.")
    
    # 1. Season Resolution
    season_res = SeasonResolver()
    num_seasons = season_res.save(out_dir)
    print(f"Master Seasons Created: {num_seasons}")
    
    # 2. Club Resolution
    club_res = ClubResolver(data_dir)
    club_res.resolve(parsed_sources)
    num_clubs, num_club_maps = club_res.save(out_dir)
    print(f"Master Clubs Created: {num_clubs}")
    print(f"Club Identity Mappings: {num_club_maps}")
    
    # 3. Player Resolution
    player_res = PlayerResolver(data_dir)
    player_res.resolve(parsed_sources, club_res.master_clubs)
    num_players, num_player_maps, num_reviews = player_res.save(out_dir)
    print(f"Master Players Created: {num_players}")
    print(f"Player Identity Mappings: {num_player_maps}")
    print(f"Players in Review Queue: {num_reviews}")
    
    print("\nResolution Output saved to /data/entity_resolution/")

if __name__ == "__main__":
    run()
