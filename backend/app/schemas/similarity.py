from pydantic import BaseModel
from typing import List, Dict, Optional

class SimilarPlayer(BaseModel):
    player_id: str
    player_name: str
    season: str
    similarity_score: float
    position: str
    feature_coverage: float
    historical_transfer_fee: Optional[float] = None

class SimilarityResponse(BaseModel):
    player: Dict
    results: List[SimilarPlayer]

class ProfileSimilarityRequest(BaseModel):
    position: str
    age_at_transfer: float = 25
    t1_minutes: float = 1000
    t1_goals_per90: float = 0
    t1_assists_per90: float = 0
    t1_bps_per90: float = 0
    career_minutes_before_transfer: float = 1000
    selling_club_pts_t1: float = 50
