import joblib
from pathlib import Path
import logging
from ml.prediction.what_if import WhatIfSimulator
from ml.similarity.engine import PlayerSimilarityEngine
import pandas as pd
import math

logger = logging.getLogger(__name__)

class ModelService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ModelService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, data_path: Path, models_dir: Path, enrichment_service=None):
        if self._initialized:
            return
            
        logger.info("Initializing ModelService and loading frozen artifacts...")
        self.data_path = data_path
        self.models_dir = models_dir
        self.enrichment_service = enrichment_service
        
        # Verify critical files exist before trying to load
        ensemble_path = models_dir / "ensemble/ensemble_metadata.joblib"
        preprocessor_path = models_dir / "preprocessors/final_preprocessor.joblib"
        similarity_data_path = data_path / "transfer_features_enriched_v2.csv"
        transfer_data_path = data_path / "transfers_normalized.csv"
        clubs_data_path = data_path / "clubs.csv"
        
        for p in [ensemble_path, preprocessor_path, similarity_data_path, transfer_data_path]:
            if not p.exists():
                raise RuntimeError(f"Missing required Phase 12/13 artifact: {p}")
                
        # Load club mapping
        self.club_map = {}
        if clubs_data_path.exists():
            try:
                clubs_df = pd.read_csv(clubs_data_path)
                for _, row in clubs_df.iterrows():
                    self.club_map[row['master_club_id']] = row['canonical_name']
                logger.info(f"Loaded {len(self.club_map)} club mappings")
            except Exception as e:
                logger.error(f"Error loading clubs: {e}")

        # Initialize ML engines
        self.simulator = WhatIfSimulator(data_path=similarity_data_path, models_dir=models_dir)
        self.similarity_engine = PlayerSimilarityEngine(data_path=similarity_data_path)
        
        # Load the raw dataset to provide player information/search
        self.df = self.simulator.df
        
        # Load transfer dataset
        self.transfers_df = pd.read_csv(transfer_data_path)
        # Merge canonical names if needed
        players = pd.read_csv(data_path / "players.csv")
        if 'canonical_name' not in self.transfers_df.columns:
             self.transfers_df = self.transfers_df.merge(players[["master_player_id", "canonical_name"]], on="master_player_id", how="left")
             
        self._initialized = True
        logger.info("ModelService initialized successfully.")

    def resolve_club_name(self, club_id: str) -> str:
        if not club_id or club_id == 'UNKNOWN':
            return None
        return self.club_map.get(club_id)

    def is_healthy(self):
        return self._initialized and hasattr(self, 'simulator') and hasattr(self, 'similarity_engine')

    def get_player_by_id(self, player_id: str):
        # Return recent seasons for player
        player_rows = self.df[self.df["master_player_id"] == player_id]
        if player_rows.empty:
            return None
            
        # Get transfers
        transfers = self.transfers_df[self.transfers_df["master_player_id"] == player_id].copy()
        
        # Map club names for transfers
        transfers['seller_club'] = transfers['from_club_id'].apply(lambda x: self.club_map.get(x, 'UNKNOWN'))
        transfers['buyer_club'] = transfers['to_club_id'].apply(lambda x: self.club_map.get(x, 'UNKNOWN'))
        
        # Try to infer current club from latest transfer if 'club' column doesn't exist
        clubs_list = []
        if "club" in player_rows.columns:
            clubs_list = player_rows["club"].unique().tolist()
            
        if not clubs_list or all(not c for c in clubs_list) or all(c == 'UNKNOWN' for c in clubs_list):
            # Fall back to inferring from transfers
            if not transfers.empty:
                # Sort by date to get the latest
                sorted_tx = transfers.sort_values(by='transfer_date')
                latest_tx = sorted_tx.iloc[-1]
                clubs_list = [latest_tx['buyer_club']]
                if latest_tx['buyer_club'] == 'UNKNOWN':
                    clubs_list = [latest_tx['seller_club']]
        
        return {
            "player_id": player_id,
            "player_name": player_rows.iloc[0].get("canonical_name", player_id),
            "position": player_rows.iloc[0].get("position", "Unknown"),
            "seasons": player_rows["season_id"].tolist(),
            "clubs": clubs_list,
            "transfer_history": transfers.to_dict(orient="records")
        }
        
    def get_market_analysis(self, season: str = None, position: str = None):
        df = self.transfers_df
        if season:
            df = df[df['season_id'] == season]
        if position:
            df = df[df['position'] == position]
            
        total_transfers = len(df)
        disclosed = df[df['fee_gbp'] > 0]
        
        return {
            "total_transfers": total_transfers,
            "disclosed_transfers": len(disclosed),
            "median_fee": float(disclosed['fee_gbp'].median()) if not disclosed.empty else 0.0,
            "mean_fee": float(disclosed['fee_gbp'].mean()) if not disclosed.empty else 0.0
        }
