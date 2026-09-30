from fastapi import APIRouter, Depends
from backend.app.dependencies import get_model_service
from backend.app.services.model_service import ModelService

router = APIRouter()

@router.get("/health")
async def health_check(service: ModelService = Depends(get_model_service)):
    return {
        "status": "ok",
        "model_loaded": service.is_healthy(),
        "similarity_engine_loaded": service.is_healthy(),
        "simulation_engine_loaded": service.is_healthy()
    }
