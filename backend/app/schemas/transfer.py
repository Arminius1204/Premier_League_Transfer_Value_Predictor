from pydantic import BaseModel
from typing import List, Dict, Optional
from backend.app.schemas.common import Pagination

class TransferResponse(Pagination):
    items: List[Dict]

class MarketAnalysisResponse(BaseModel):
    total_transfers: int
    disclosed_transfers: int
    median_fee: float
    mean_fee: float
