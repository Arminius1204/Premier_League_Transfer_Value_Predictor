import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path
import logging
from dotenv import load_dotenv

# Add backend to path to import client
sys.path.append(str(Path(__file__).resolve().parent.parent))
from backend.app.services.api_football_client import APIFootballClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_enrichment():
    load_dotenv()
    api_key = os.getenv('API_FOOTBALL_KEY', '6e027925921f11a7c4b2152583de1eeb')
    
    base_dir = Path(__file__).resolve().parent.parent
    metadata_path = base_dir / 'data' / 'player_enrichment' / 'player_metadata.csv'
    review_queue_path = base_dir / 'data' / 'player_enrichment' / 'review_queue.csv'
    cache_dir = base_dir / 'data' / 'player_enrichment' / 'api_cache'
    
    if not metadata_path.exists():
        logger.error(f"Metadata file not found at {metadata_path}. Run enrichment_builder.py first.")
        return
        
    df = pd.read_csv(metadata_path, encoding='utf-8')
    
    if not api_key:
        logger.warning("No API_FOOTBALL_KEY provided. Enrichment will skip API calls.")
        # Print summary
        logger.info(f"Total players in metadata: {len(df)}")
        return
        
    client = APIFootballClient(api_key=api_key, cache_dir=cache_dir)
    
    unresolved = []
    
    # Process only players missing position or photo_url
    mask_to_enrich = df['position'].isna() | df['photo_url'].isna()
    players_to_enrich = df[mask_to_enrich]
    
    logger.info(f"Found {len(players_to_enrich)} players needing enrichment")
    
    for idx, row in players_to_enrich.iterrows():
        name = row['canonical_name']
        logger.info(f"Enriching {name} ({row['master_player_id']})")
        
        results = client.search_player(name)
        
        match_found = False
        if results:
            # Simple matching logic: exact name match (case-insensitive)
            # In a real scenario, this would use fuzzy matching + nationality + age
            for res in results:
                if res['canonical_name'].lower() == name.lower():
                    # Auto-accept
                    df.at[idx, 'position'] = res['position']
                    df.at[idx, 'nationality'] = res['nationality']
                    df.at[idx, 'date_of_birth'] = res['date_of_birth']
                    df.at[idx, 'photo_url'] = res['photo_url']
                    df.at[idx, 'external_provider'] = 'api-football'
                    df.at[idx, 'external_player_id'] = res['external_player_id']
                    df.at[idx, 'match_status'] = 'EXACT'
                    df.at[idx, 'match_confidence'] = 'HIGH'
                    match_found = True
                    break
        
        if not match_found:
            unresolved.append(row.to_dict())
            
    # Save metadata
    df.to_csv(metadata_path, index=False, encoding='utf-8')
    logger.info(f"Updated metadata saved to {metadata_path}")
    
    if unresolved:
        unresolved_df = pd.DataFrame(unresolved)
        unresolved_df.to_csv(review_queue_path, index=False, encoding='utf-8')
        logger.info(f"Wrote {len(unresolved)} unresolved players to {review_queue_path}")
        
if __name__ == "__main__":
    run_enrichment()
