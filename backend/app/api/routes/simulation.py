from fastapi import APIRouter, Depends, HTTPException
from backend.app.dependencies import get_model_service
from backend.app.services.model_service import ModelService
from backend.app.schemas.simulation import SimulationRequest, SimulationResponse

router = APIRouter()

@router.post("/simulate", response_model=SimulationResponse)
async def simulate_what_if(req: SimulationRequest, service: ModelService = Depends(get_model_service)):
    # Validate features exist
    for k in req.changes.keys():
        if k not in service.simulator.features:
            raise HTTPException(status_code=422, detail=f"Unsupported scenario feature: {k}")
            
    try:
        res = service.simulator.simulate(req.player_id, req.season, req.changes)
        
        return {
            "player_id": req.player_id,
            "baseline": {
                "prediction": res["Baseline Prediction"],
                "lower_bound": res["Baseline Interval (80%)"][0],
                "upper_bound": res["Baseline Interval (80%)"][1]
            },
            "scenario": {
                "prediction": res["Scenario Prediction"],
                "lower_bound": res["Scenario Interval (80%)"][0],
                "upper_bound": res["Scenario Interval (80%)"][1]
            },
            "absolute_change": res["Absolute Change"],
            "percentage_change": res["Percentage Change"],
            "changed_features": req.changes,
            "warnings": res["OOD Warnings"]
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Simulation failed")

@router.post("/predict")
async def direct_predict(features: dict, service: ModelService = Depends(get_model_service)):
    # Direct prediction from a raw feature dict
    try:
        # Check missing mandatory features
        for f in service.simulator.features:
            if f not in features:
                features[f] = 0 # Defaulting for API robustness if not provided fully
                
        preds = service.simulator.predict(features)
        
        # Determine OOD warnings
        ood_warnings = service.simulator._check_ood(features)
        
        return {
            "prediction": preds["prediction"],
            "lower_bound": preds["lower_bound_80"],
            "upper_bound": preds["upper_bound_80"],
            "model_information": "weighted_ensemble",
            "uncertainty_information": "conformal_prediction",
            "feature_coverage": 1.0,
            "warnings": ood_warnings
        }
    except Exception as e:
        raise HTTPException(status_code=422, detail="Invalid input for prediction")
