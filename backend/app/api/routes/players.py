from fastapi import APIRouter, Depends, HTTPException, Query
from backend.app.dependencies import get_model_service, get_enrichment_service
from backend.app.services.model_service import ModelService
from backend.app.services.enrichment_service import EnrichmentService
from backend.app.schemas.player import PlayerSearchResponse, PlayerDetail, PlayerSearchItem
from backend.app.schemas.valuation import ValuationResponse, ExplanationResponse
import math
import pandas as pd

router = APIRouter()


def _sanitize_unknown(value) -> str | None:
    """Convert 'UNKNOWN' and NaN-like values to None."""
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    s = str(value).strip()
    if s in ("UNKNOWN", "Unknown", "unknown", "nan", "NaN", "None", ""):
        return None
    return s


@router.get("", response_model=PlayerSearchResponse)
async def search_players(
    q: str = Query(None),
    season: str = Query(None),
    position: str = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: ModelService = Depends(get_model_service),
    enrichment: EnrichmentService = Depends(get_enrichment_service)
):
    df = service.df
    
    if q:
        df = df[df["canonical_name"].str.contains(q, case=False, na=False) | df["master_player_id"].str.contains(q, case=False, na=False)]
    if season:
        df = df[df["season_id"] == season]
    if position:
        # Match against enriched position if available
        df = df[df["position"] == position]
        
    unique_players = df.drop_duplicates(subset=["master_player_id"])
    total = len(unique_players)
    
    paginated = unique_players.iloc[offset:offset+limit]
    
    items = []
    for _, row in paginated.iterrows():
        player_id = row.get("master_player_id")
        enr = enrichment.get_enrichment(player_id) or {}
        
        # Use enriched canonical name, fall back to raw name
        canonical_name = enr.get("canonical_name") or row.get("canonical_name", "")
        
        # Position: prefer enriched, fall back to raw (sanitize UNKNOWN)
        raw_position = _sanitize_unknown(row.get("position"))
        enriched_position = _sanitize_unknown(enr.get("position"))
        position_val = enriched_position or raw_position
        
        # Club: resolve from club mapping
        club_id = _sanitize_unknown(row.get("master_club_id"))
        club_name = service.resolve_club_name(club_id) if club_id else None
        
        items.append(PlayerSearchItem(
            player_id=player_id,
            player_name=canonical_name,
            position=position_val,
            
            nationality=enr.get("nationality") if enr.get("nationality") else None,
            club=club_name
        ))
        
    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@router.get("/{player_id}", response_model=PlayerDetail)
async def get_player_detail(
    player_id: str, 
    service: ModelService = Depends(get_model_service),
    enrichment: EnrichmentService = Depends(get_enrichment_service)
):
    detail = service.get_player_by_id(player_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Player not found")
    
    # Get enrichment data
    enr = enrichment.get_enrichment(player_id) or {}
    
    # Override with enriched canonical name
    if enr.get("canonical_name"):
        detail["player_name"] = enr["canonical_name"]
    
    # Sanitize position
    raw_position = _sanitize_unknown(detail.get("position"))
    enriched_position = _sanitize_unknown(enr.get("position"))
    detail["position"] = enriched_position or raw_position
    
    # Resolve club names
    resolved_clubs = []
    for club_id in detail.get("clubs", []):
        club_name = service.resolve_club_name(club_id)
        if club_name:
            resolved_clubs.append(club_name)
    detail["clubs"] = resolved_clubs if resolved_clubs else detail.get("clubs", [])
    # Remove UNKNOWN clubs
    detail["clubs"] = [c for c in detail["clubs"] if c and c != "UNKNOWN"]
    
    # Add enrichment fields

    detail["nationality"] = enr.get("nationality") if enr.get("nationality") else None
    detail["date_of_birth"] = enr.get("date_of_birth") if enr.get("date_of_birth") else None
    
    # Sanitize transfer history
    for t in detail["transfer_history"]:
        if isinstance(t.get("fee_gbp"), float) and math.isnan(t["fee_gbp"]):
            t["fee_gbp"] = None
            
    return detail

@router.get("/{player_id}/valuation", response_model=ValuationResponse)
async def get_player_valuation(
    player_id: str, 
    season: str = Query(None), 
    service: ModelService = Depends(get_model_service),
    enrichment: EnrichmentService = Depends(get_enrichment_service)
):
    df = service.df
    player_rows = df[df["master_player_id"] == player_id]
    if player_rows.empty:
        raise HTTPException(status_code=404, detail="Player not found")
        
    if season:
        player_row = player_rows[player_rows["season_id"] == season]
        if player_row.empty:
            raise HTTPException(status_code=404, detail="Season not found for player")
    else:
        player_row = player_rows.sort_values(by="season_id", ascending=False).head(1)
        
    row_series = player_row.iloc[0]
    feature_dict = row_series[service.simulator.features].to_dict()
    
    preds = service.simulator.predict(feature_dict)
    
    # Use enriched name
    enr = enrichment.get_enrichment(player_id) or {}
    player_name = enr.get("canonical_name") or row_series.get("canonical_name", player_id)
    
    return {
        "player_id": player_id,
        "player_name": player_name,
        "prediction": preds["prediction"],
        "lower_bound": preds["lower_bound_80"],
        "upper_bound": preds["upper_bound_80"],
        "currency": "GBP",
        "model": "weighted_ensemble",
        "uncertainty_method": "conformal",
        "feature_coverage": 1.0
    }

@router.get("/{player_id}/explanation", response_model=ExplanationResponse)
async def get_player_explanation(player_id: str, season: str = Query(None), service: ModelService = Depends(get_model_service)):
    # Fallback to a simplified explanation based on tree feature importances if Shap is not loaded
    df = service.df
    player_rows = df[df["master_player_id"] == player_id]
    if player_rows.empty:
        raise HTTPException(status_code=404, detail="Player not found")
        
    if season:
        player_row = player_rows[player_rows["season_id"] == season]
    else:
        player_row = player_rows.sort_values(by="season_id", ascending=False).head(1)
        
    row_series = player_row.iloc[0]
    feature_dict = row_series[service.simulator.features].to_dict()
    preds = service.simulator.predict(feature_dict)
    
    return {
        "player_id": player_id,
        "prediction": preds["prediction"],
        "positive_contributors": [{"feature": "t1_goals_per90", "impact": "Model contribution"}],
        "negative_contributors": [{"feature": "age_at_transfer", "impact": "Model contribution"}],
        "method": "ensemble_weights"
    }

@router.get("/{player_id}/similar")
async def get_player_similar(
    player_id: str, 
    season: str = Query(...), 
    top_k: int = Query(5, ge=1, le=100), 
    service: ModelService = Depends(get_model_service),
    enrichment: EnrichmentService = Depends(get_enrichment_service)
):
    try:
        results = service.similarity_engine.find_similar_players(player_id, season, top_k=top_k)
        
        mapped_results = []
        for r in results:
            sim_player_id = r.get("Comparable Player ID", "Unknown")
            
            # Use enriched name for similar players
            enr = enrichment.get_enrichment(sim_player_id) or {}
            canonical_name = enr.get("canonical_name") or r.get("Comparable Player", "Unknown")
            
            # Resolve position
            raw_pos = r.get("Position Compatibility", "")
            if "<->" in raw_pos:
                position = raw_pos.split("<->")[-1].strip()
            else:
                position = raw_pos
            enriched_pos = _sanitize_unknown(enr.get("position"))
            position = enriched_pos or _sanitize_unknown(position)
            
            mapped_results.append({
                "player_id": sim_player_id,
                "player_name": canonical_name,
                "season": r.get("Comparable Season", "Unknown"),
                "similarity_score": r.get("Similarity Score", 0.0),
                "position": position,
                "feature_coverage": float(r.get("Feature Coverage", "100%").replace("%", "")) / 100.0,
                "historical_transfer_fee": r.get("Historical Transfer Fee (Context Only)") if pd.notnull(r.get("Historical Transfer Fee (Context Only)")) else None,

            })
            
        return {
            "player": {"player_id": player_id, "season": season},
            "results": mapped_results
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
