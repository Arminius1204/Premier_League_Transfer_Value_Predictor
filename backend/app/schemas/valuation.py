from pydantic import BaseModel
from typing import List, Dict, Optional

class ValuationResponse(BaseModel):
    player_id: str
    player_name: str
    prediction: float
    lower_bound: float
    upper_bound: float
    currency: str = "GBP"
    model: str = "weighted_ensemble"
    uncertainty_method: str = "conformal"
    feature_coverage: Optional[float] = None

class ExplanationResponse(BaseModel):
    player_id: str
    prediction: float
    positive_contributors: List[Dict]
    negative_contributors: List[Dict]
    method: str
