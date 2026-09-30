from fastapi import APIRouter, Depends, HTTPException
from backend.app.dependencies import get_model_service
from backend.app.services.model_service import ModelService
from backend.app.schemas.similarity import ProfileSimilarityRequest, SimilarPlayer
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

router = APIRouter()

@router.post("/profile")
async def profile_similarity(req: ProfileSimilarityRequest, service: ModelService = Depends(get_model_service)):
    # Validate position is supported
    if req.position not in service.similarity_engine.scalers:
        raise HTTPException(status_code=422, detail=f"Unsupported position: {req.position}")
        
    engine = service.similarity_engine
    
    # 1. Scale input profile
    profile_dict = req.dict()
    profile_vec = [profile_dict.get(f, 0) for f in engine.sim_features]
    
    scaler = engine.scalers[req.position]
    scaled_profile = scaler.transform([profile_vec])
    
    # 2. Get subset for position
    df_pos = engine.imputed_df[engine.imputed_df['position'] == req.position]
    if df_pos.empty:
        return {"results": []}
        
    # 3. Calculate cosine similarity
    X = df_pos[engine.sim_features].values
    sims = cosine_similarity(scaled_profile, X)[0]
    
    # 4. Get top-K
    top_k_indices = np.argsort(sims)[::-1][:5]
    
    results = []
    for idx in top_k_indices:
        row = df_pos.iloc[idx]
        results.append({
            "player_id": row["master_player_id"],
            "player_name": row.get("canonical_name", row["master_player_id"]),
            "season": row["season_id"],
            "similarity_score": float(sims[idx]),
            "position": row["position"],
            "feature_coverage": float(row.get("feature_coverage", 1.0)),
            "historical_transfer_fee": float(row["fee_gbp"]) if pd.notnull(row["fee_gbp"]) else None
        })
        
    return {"results": results}
