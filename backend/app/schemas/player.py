from pydantic import BaseModel
from typing import List, Optional, Dict
from backend.app.schemas.common import Pagination

class TransferRecord(BaseModel):
    season_id: Optional[str] = None
    transfer_type: Optional[str] = None
    fee_gbp: Optional[float] = None
    buyer_club: Optional[str] = None
    seller_club: Optional[str] = None

class PlayerSearchItem(BaseModel):
    player_id: str
    player_name: str
    master_player_id: Optional[str] = None
    canonical_name: Optional[str] = None
    display_name: Optional[str] = None
    position: Optional[str] = None
    club: Optional[str] = None
    club_id: Optional[str] = None
    season: Optional[str] = None
    nationality: Optional[str] = None
    date_of_birth: Optional[str] = None
    transfer_context: Optional[str] = None
    metadata_source: Optional[str] = None
    metadata_confidence: Optional[float] = None

class PlayerDetail(BaseModel):
    player_id: str
    player_name: str
    master_player_id: Optional[str] = None
    canonical_name: Optional[str] = None
    display_name: Optional[str] = None
    position: Optional[str] = None
    seasons: List[str]
    clubs: List[str]
    club: Optional[str] = None
    club_id: Optional[str] = None
    transfer_history: List[TransferRecord]
    nationality: Optional[str] = None
    date_of_birth: Optional[str] = None
    metadata_source: Optional[str] = None
    metadata_confidence: Optional[float] = None

class PlayerSearchResponse(Pagination):
    items: List[PlayerSearchItem]
