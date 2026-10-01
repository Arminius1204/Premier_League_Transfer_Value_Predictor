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
