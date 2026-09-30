from fastapi import APIRouter, Depends
from backend.app.dependencies import get_model_service
from backend.app.services.model_service import ModelService

router = APIRouter()

@router.get("")
async def get_model_info(service: ModelService = Depends(get_model_service)):
    meta = service.simulator.meta
    
    return {
        "production_model": "weighted_ensemble",
        "candidate_models": ["Ridge", "RandomForest", "XGBoost"],
        "ensemble_information": {
            "weights": meta.get("weights", {}),
            "method": "weighted_average"
        },
        "validation_methodology": "walk_forward_cv",
        "metrics": {
            "MAE": meta.get("ensemble_metrics", {}).get("mae", 0),
            "RMSE": meta.get("ensemble_metrics", {}).get("rmse", 0),
            "R2": meta.get("ensemble_metrics", {}).get("r2", 0),
            "median_absolute_error": meta.get("ensemble_metrics", {}).get("medae", 0)
        },
        "uncertainty_methodology": "conformal_prediction",
        "training_period": meta.get("training_period", "Unknown"),
        "final_holdout_period": meta.get("final_holdout_period", "Unknown")
    }
