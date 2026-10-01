from pydantic import BaseModel
from typing import List, Dict, Optional

class SimulationRequest(BaseModel):
    player_id: str
    season: str
    changes: Dict[str, float]

class SimulationBounds(BaseModel):
    prediction: float
    lower_bound: float
    upper_bound: float

class SimulationResponse(BaseModel):
    player_id: str
    baseline: SimulationBounds
    scenario: SimulationBounds
    absolute_change: float
    percentage_change: float
    changed_features: Dict[str, float]
    warnings: List[str]
    ood: bool = False
    ood_features: List[str] = []
    interpretation: str = "sensitivity_analysis_not_causal"

