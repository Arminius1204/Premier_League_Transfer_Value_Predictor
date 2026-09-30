from fastapi import APIRouter, Depends, Query
from backend.app.dependencies import get_model_service
from backend.app.services.model_service import ModelService
from backend.app.schemas.transfer import MarketAnalysisResponse

router = APIRouter()

@router.get("", response_model=MarketAnalysisResponse)
async def get_market_analysis(
    season: str = Query(None),
    position: str = Query(None),
    service: ModelService = Depends(get_model_service)
):
    return service.get_market_analysis(season=season, position=position)
