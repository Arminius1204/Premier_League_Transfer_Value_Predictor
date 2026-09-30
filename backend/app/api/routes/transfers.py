from fastapi import APIRouter, Depends, Query
from backend.app.dependencies import get_model_service
from backend.app.services.model_service import ModelService
from backend.app.schemas.transfer import TransferResponse
import math

router = APIRouter()

@router.get("", response_model=TransferResponse)
async def get_transfers(
    season: str = Query(None),
    club: str = Query(None),
    player: str = Query(None),
    position: str = Query(None),
    min_fee: float = Query(None),
    max_fee: float = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: ModelService = Depends(get_model_service)
):
    df = service.transfers_df
    
    if season:
        df = df[df["season_id"] == season]
    if club:
        df = df[(df["buyer_club"].str.contains(club, case=False, na=False)) | (df["seller_club"].str.contains(club, case=False, na=False))]
    if player:
        df = df[df["canonical_name"].str.contains(player, case=False, na=False) | df["master_player_id"].str.contains(player, case=False, na=False)]
    if position:
        df = df[df["position"] == position]
    if min_fee is not None:
        df = df[df["fee_gbp"] >= min_fee]
    if max_fee is not None:
        df = df[df["fee_gbp"] <= max_fee]
        
    total = len(df)
    paginated = df.iloc[offset:offset+limit]
    
    items = []
    for _, row in paginated.iterrows():
        # Handle nan for undisclosed
        fee = row.get("fee_gbp")
        if isinstance(fee, float) and math.isnan(fee):
            fee = None
            
        items.append({
            "player_id": row.get("master_player_id"),
            "player_name": row.get("canonical_name"),
            "season_id": row.get("season_id"),
            "transfer_type": row.get("transfer_type"),
            "fee_gbp": fee,
            "buyer_club": row.get("buyer_club"),
            "seller_club": row.get("seller_club")
        })
        
    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset
    }
