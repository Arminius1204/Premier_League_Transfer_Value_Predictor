import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_enrichment_data(
    identity_map_path: Path,
    output_path: Path
):
    """
    Build initial player metadata from identity map.
    """
    logger.info(f"Loading identity map from {identity_map_path}")
    if not identity_map_path.exists():
        logger.error(f"Identity map not found at {identity_map_path}")
        return

    df = pd.read_csv(identity_map_path, encoding='utf-8')
    
    # We want one row per master_player_id
    # We prefer transfermarkt names, then FPL names
    
    # Sort so transfermarkt is first for each player
    df['source_priority'] = df['source'].map({'transfermarkt': 0, 'fpl': 1}).fillna(2)
    df = df.sort_values(['master_player_id', 'source_priority'])
    
    # Drop duplicates to keep highest priority source
    unique_players = df.drop_duplicates('master_player_id', keep='first').copy()
    
    # Build output dataframe
    metadata = pd.DataFrame()
    metadata['master_player_id'] = unique_players['master_player_id']
    metadata['canonical_name'] = unique_players['source_player_name']
    metadata['position'] = None
    metadata['nationality'] = None
    metadata['date_of_birth'] = None
    metadata['photo_url'] = None
    
    # Set external provider to transfermarkt if source is transfermarkt
    is_tm = unique_players['source'] == 'transfermarkt'
    metadata['external_provider'] = np.where(is_tm, 'transfermarkt', None)
    metadata['external_player_id'] = np.where(is_tm, unique_players['source_player_id'], None)
    
    metadata['match_status'] = 'EXACT'
    metadata['match_confidence'] = 'HIGH'
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Writing {len(metadata)} enrichment records to {output_path}")
    metadata.to_csv(output_path, index=False, encoding='utf-8')
    logger.info("Enrichment data generated successfully")

if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    identity_map = base_dir / 'data' / 'entity_resolution' / 'player_identity_map.csv'
    output = base_dir / 'data' / 'player_enrichment' / 'player_metadata.csv'
    build_enrichment_data(identity_map, output)
