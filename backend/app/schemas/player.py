from pydantic import BaseModel
from typing import List, Optional, Dict
from backend.app.schemas.common import Pagination

class TransferRecord(BaseModel):
    season_id: Optional[str] = None
    transfer_type: Optional[str] = None
    fee_gbp: Optional[float] = None
    buyer_club: Optional[str] = None
    seller_club: Optional[str] = None

class PlayerDetail(BaseModel):
    player_id: str
    player_name: str
    position: str
    seasons: List[str]
    clubs: List[str]
    transfer_history: List[TransferRecord]

class PlayerSearchResponse(Pagination):
    items: List[Dict]
