import pandas as pd
from pathlib import Path
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class ClubResolver:
    def __init__(self, clubs_csv_path: Path):
        self.clubs_csv_path = clubs_csv_path
        self.club_map: Dict[str, str] = {}
        self._load_clubs()

    def _load_clubs(self):
        """Load club mappings from CSV."""
        if not self.clubs_csv_path.exists():
            logger.warning(f"Clubs file not found at {self.clubs_csv_path}")
            return

        try:
            df = pd.read_csv(self.clubs_csv_path, encoding='utf-8')
            for _, row in df.iterrows():
                self.club_map[row['master_club_id']] = row['canonical_name']
            logger.info(f"Loaded {len(self.club_map)} club mappings")
        except Exception as e:
            logger.error(f"Failed to load clubs data: {e}")

    def resolve_club(self, club_id: str) -> Optional[str]:
        """Resolve master_club_id to canonical club name."""
        if not club_id or club_id == 'UNKNOWN':
            return None
        return self.club_map.get(club_id)
        
    def get_season_club(self, player_id: str, season_id: str) -> Optional[str]:
        """Resolve club for a player in a specific season using player_season_clubs.csv."""
        # For a full implementation, we'd load the file into memory.
        # Since this is a lightweight resolution service, we'll try to find it.
        mapping_path = self.clubs_csv_path.parent / 'player_season_clubs.csv'
        if not mapping_path.exists():
            return None
            
        try:
            # Note: in a production app this would be cached in a dict
            df = pd.read_csv(mapping_path)
            mask = (df['master_player_id'] == player_id) & (df['season_id'] == season_id)
            if mask.any():
                club_id = df[mask].iloc[0]['master_club_id']
                return self.resolve_club(club_id)
        except Exception as e:
            logger.error(f"Failed to lookup season club: {e}")
            
        return None
