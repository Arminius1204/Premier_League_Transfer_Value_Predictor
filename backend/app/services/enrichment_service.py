import pandas as pd
from pathlib import Path
import logging
from typing import Dict, Optional
import math

logger = logging.getLogger(__name__)


def _nan_to_none(value):
    """Convert NaN/NaT/empty values to Python None."""
    if value is None:
        return None
    if isinstance(value, float) and (math.isnan(value) or pd.isna(value)):
        return None
    if isinstance(value, str) and value.strip() in ("", "nan", "NaN", "NaT"):
        return None
    return value


class EnrichmentService:
    def __init__(self, metadata_path: Path):
        self.metadata_path = metadata_path
        self.enrichments: Dict[str, Dict] = {}
        self._load_enrichments()

    def _load_enrichments(self):
        """Load player enrichment metadata from CSV."""
        if not self.metadata_path.exists():
            logger.warning(f"Enrichment metadata not found at {self.metadata_path}")
            return

        try:
            df = pd.read_csv(self.metadata_path, encoding='utf-8')
            
            for _, row in df.iterrows():
                record = {}
                for col in df.columns:
                    record[col] = _nan_to_none(row[col])
                self.enrichments[row['master_player_id']] = record
                
            logger.info(f"Loaded {len(self.enrichments)} player enrichments")
        except Exception as e:
            logger.error(f"Failed to load enrichment data: {e}")

    def get_enrichment(self, player_id: str) -> Optional[Dict]:
        """Get enrichment data for a specific player."""
        return self.enrichments.get(player_id)

    def get_all_enrichments(self) -> Dict[str, Dict]:
        """Get all player enrichments."""
        return self.enrichments
