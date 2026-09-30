import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

class PlayerSimilarityEngine:
    def __init__(self, data_path: Path):
        self.df = pd.read_csv(data_path)
        
        # Merge player names for readability
        players = pd.read_csv(data_path.parent / "players.csv")
        self.df = self.df.merge(players[["master_player_id", "canonical_name"]], on="master_player_id", how="left")
        
        # Define similarity features (EXPLICITLY EXCLUDING FEE AND IDs)
        self.sim_features = [
            'age_at_transfer', 't1_minutes', 't1_goals_per90', 
            't1_assists_per90', 't1_bps_per90', 'career_minutes_before_transfer',
            'selling_club_pts_t1'
        ]
        
        # Keep context columns separate
        self.context_cols = ['master_player_id', 'canonical_name', 'season_id', 'position', 'fee_gbp']
        
        self.scalers = {}
        self.imputed_df = self._prepare_data()

    def _prepare_data(self):
        # We handle missing data via median imputation WITHIN positions
        imputed = self.df.copy()
        imputed[self.sim_features] = imputed[self.sim_features].astype(float)
        
        for pos in imputed['position'].unique():
            pos_mask = imputed['position'] == pos
            
            # Median impute
            medians = imputed.loc[pos_mask, self.sim_features].median()
            # If a position has entirely missing data for a column, fill with global median
            medians = medians.fillna(imputed[self.sim_features].median())
            # If STILL missing, 0
            medians = medians.fillna(0)
            
            imputed.loc[pos_mask, self.sim_features] = imputed.loc[pos_mask, self.sim_features].fillna(medians)
            
            # Scale
            scaler = StandardScaler()
            imputed.loc[pos_mask, self.sim_features] = scaler.fit_transform(imputed.loc[pos_mask, self.sim_features])
            self.scalers[pos] = scaler
            
        # Calculate coverage (how many features were originally non-null)
        coverage = self.df[self.sim_features].notnull().sum(axis=1) / len(self.sim_features)
        imputed['feature_coverage'] = coverage
        return imputed

    def find_similar_players(self, player_id: str, season: str, top_k: int = 5):
        query_mask = (self.imputed_df['master_player_id'] == player_id) & (self.imputed_df['season_id'] == season)
        if not query_mask.any():
            raise ValueError("Player/Season combination not found.")
            
        query_row = self.imputed_df[query_mask].iloc[0]
        pos = query_row['position']
        
        # Filter to same position
        pool = self.imputed_df[self.imputed_df['position'] == pos].copy()
        # Drop the queried player from pool
        pool = pool[~((pool['master_player_id'] == player_id) & (pool['season_id'] == season))]
        
        if pool.empty:
            return []
            
        q_vec = query_row[self.sim_features].values.reshape(1, -1)
        p_vecs = pool[self.sim_features].values
        
        sims = cosine_similarity(q_vec, p_vecs)[0]
        pool['similarity_score'] = sims
        
        top_pool = pool.sort_values('similarity_score', ascending=False).head(top_k)
        
        results = []
        for _, row in top_pool.iterrows():
            results.append({
                "Queried Player": query_row["canonical_name"],
                "Queried Season": query_row["season_id"],
                "Comparable Player": row["canonical_name"],
                "Comparable Season": row["season_id"],
                "Similarity Score": round(row["similarity_score"], 4),
                "Position Compatibility": f"{query_row['position']} <-> {row['position']}",
                "Feature Coverage": f"{row['feature_coverage']*100:.1f}%",
                "Historical Transfer Fee (Context Only)": row["fee_gbp"]
            })
            
        return results

    def compare_profile_to_dataset(self, profile: dict, top_k: int = 5):
        pos = profile.get('position', 'UNKNOWN')
        if pos not in self.scalers:
            raise ValueError(f"Unknown position: {pos}")
            
        # Build query vector using position medians for missing
        q_raw = []
        coverage_count = 0
        medians = self.df[self.df['position'] == pos][self.sim_features].median().fillna(0)
        
        for f in self.sim_features:
            if f in profile and pd.notnull(profile[f]):
                q_raw.append(profile[f])
                coverage_count += 1
            else:
                q_raw.append(medians[f])
                
        q_raw = np.array(q_raw).reshape(1, -1)
        q_scaled = self.scalers[pos].transform(q_raw)
        
        pool = self.imputed_df[self.imputed_df['position'] == pos].copy()
        if pool.empty:
            return []
            
        sims = cosine_similarity(q_scaled, pool[self.sim_features].values)[0]
        pool['similarity_score'] = sims
        top_pool = pool.sort_values('similarity_score', ascending=False).head(top_k)
        
        results = []
        for _, row in top_pool.iterrows():
            results.append({
                "Queried Player": "Hypothetical Profile",
                "Queried Season": "N/A",
                "Comparable Player": row["canonical_name"],
                "Comparable Season": row["season_id"],
                "Similarity Score": round(row["similarity_score"], 4),
                "Position Compatibility": f"{pos} <-> {row['position']}",
                "Feature Coverage": f"{row['feature_coverage']*100:.1f}%",
                "Historical Transfer Fee (Context Only)": row["fee_gbp"]
            })
        return results

    def compare_players(self, p1_id, p1_season, p2_id, p2_season):
        m1 = (self.imputed_df['master_player_id'] == p1_id) & (self.imputed_df['season_id'] == p1_season)
        m2 = (self.imputed_df['master_player_id'] == p2_id) & (self.imputed_df['season_id'] == p2_season)
        
        if not m1.any() or not m2.any():
            raise ValueError("Player/Season not found.")
            
        r1 = self.imputed_df[m1].iloc[0]
        r2 = self.imputed_df[m2].iloc[0]
        
        if r1['position'] != r2['position']:
            return 0.0 # Strict position compatibility constraint
            
        v1 = r1[self.sim_features].values.reshape(1, -1)
        v2 = r2[self.sim_features].values.reshape(1, -1)
        
        return cosine_similarity(v1, v2)[0][0]
