import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity


# --- Coverage tier definitions ---
COVERAGE_TIERS = {
    "insufficient_data": (0.0, 0.4),
    "low_coverage": (0.4, 0.6),
    "usable_with_warning": (0.6, 0.8),
    "strong_coverage": (0.8, 1.01),  # 1.01 to include 1.0
}


def _classify_coverage(coverage: float) -> str:
    """Return the human-readable coverage tier for a given ratio."""
    for tier, (lo, hi) in COVERAGE_TIERS.items():
        if lo <= coverage < hi:
            return tier
    return "insufficient_data"


class PlayerSimilarityEngine:
    def __init__(self, data_path: Path):
        self.df = pd.read_csv(data_path)

        # Merge player names for readability
        players = pd.read_csv(data_path.parent / "players.csv")
        self.df = self.df.merge(
            players[["master_player_id", "canonical_name"]],
            on="master_player_id",
            how="left",
        )

        # Define similarity features (EXPLICITLY EXCLUDING FEE AND IDs)
        self.sim_features = [
            "age_at_transfer",
            "t1_minutes",
            "t1_goals_per90",
            "t1_assists_per90",
            "t1_bps_per90",
            "career_minutes_before_transfer",
            "selling_club_pts_t1",
        ]

        # Keep context columns separate
        self.context_cols = [
            "master_player_id",
            "canonical_name",
            "season_id",
            "position",
            "fee_gbp",
        ]

        # Pre-compute reference statistics for standardisation.
        # We fit ONE global scaler on all non-null observed values so that
        # pairwise comparisons are always expressed in the same units.
        self._raw_numeric = self.df[self.sim_features].apply(
            pd.to_numeric, errors="coerce"
        )
        self._validity_mask = self._raw_numeric.notnull()

        self.global_scaler = StandardScaler()
        # Fit on all observed (non-null) values column-by-column.
        # We use a filled copy only for fitting; the mask keeps track of
        # which cells are genuine observations.
        filled_for_fit = self._raw_numeric.copy()
        for col in self.sim_features:
            col_vals = self._raw_numeric[col].dropna()
            if len(col_vals) > 0:
                filled_for_fit[col] = filled_for_fit[col].fillna(col_vals.median())
            else:
                filled_for_fit[col] = filled_for_fit[col].fillna(0.0)
        self.global_scaler.fit(filled_for_fit)

        # Scaled matrix (NaN where original was NaN)
        scaled_all = self.global_scaler.transform(filled_for_fit)
        self._scaled = pd.DataFrame(
            scaled_all, columns=self.sim_features, index=self.df.index
        )
        # Re-mask: keep NaN where the original had no observation
        for col in self.sim_features:
            self._scaled.loc[~self._validity_mask[col], col] = np.nan

        # Per-row feature coverage (fraction of non-null sim features)
        self._row_coverage = (
            self._validity_mask.sum(axis=1) / len(self.sim_features)
        )

        # Legacy attribute kept for backward compatibility with Phase 13 tests
        self.scalers = {"UNKNOWN": self.global_scaler}
        self.imputed_df = self._build_imputed_legacy()

    # ------------------------------------------------------------------
    # Legacy helper – the Phase 13 tests call compare_players / imputed_df
    # directly, so we keep a median-imputed frame available.  The NEW
    # find_similar_players path does NOT use this frame.
    # ------------------------------------------------------------------
    def _build_imputed_legacy(self):
        imputed = self.df.copy()
        imputed[self.sim_features] = self._raw_numeric
        global_medians = self._raw_numeric.median().fillna(0)
        for col in self.sim_features:
            imputed[col] = imputed[col].fillna(global_medians[col])
        imputed[self.sim_features] = self.global_scaler.transform(
            imputed[self.sim_features]
        )
        imputed["feature_coverage"] = self._row_coverage.values
        return imputed

    # ------------------------------------------------------------------
    # Pairwise missing-data-aware cosine similarity
    # ------------------------------------------------------------------
    def _pairwise_aware_similarity(self, q_idx: int, pool_indices):
        """
        For every candidate in *pool_indices*, compute cosine similarity
        against the query row at *q_idx* using ONLY features that are
        genuinely observed (non-null) in BOTH rows.

        Returns a list of dicts with:
            similarity_score, shared_features, feature_coverage, data_quality
        """
        q_scaled = self._scaled.loc[q_idx]
        q_valid = self._validity_mask.loc[q_idx]

        results = []
        for pidx in pool_indices:
            p_scaled = self._scaled.loc[pidx]
            p_valid = self._validity_mask.loc[pidx]

            # Overlap: features valid in BOTH query and candidate
            shared_mask = q_valid & p_valid
            shared_count = int(shared_mask.sum())
            overlap_ratio = shared_count / len(self.sim_features)
            tier = _classify_coverage(overlap_ratio)

            if shared_count < 1:
                results.append(
                    {
                        "index": pidx,
                        "similarity_score": 0.0,
                        "shared_features": [],
                        "feature_coverage": 0.0,
                        "data_quality": "insufficient_data",
                        "confidence": 0.0,
                    }
                )
                continue

            shared_cols = [c for c, m in zip(self.sim_features, shared_mask) if m]

            q_vec = q_scaled[shared_cols].values.reshape(1, -1)
            p_vec = p_scaled[shared_cols].values.reshape(1, -1)

            # Guard against zero-norm vectors (all observed features are
            # identical after standardisation → the vector is all-zeros).
            q_norm = np.linalg.norm(q_vec)
            p_norm = np.linalg.norm(p_vec)
            if q_norm == 0 or p_norm == 0:
                sim = 0.0
            else:
                sim = float(cosine_similarity(q_vec, p_vec)[0][0])

            # Confidence penalises low overlap
            confidence = round(overlap_ratio, 4)

            results.append(
                {
                    "index": pidx,
                    "similarity_score": round(sim, 4),
                    "shared_features": shared_cols,
                    "feature_coverage": round(overlap_ratio, 4),
                    "data_quality": tier,
                    "confidence": confidence,
                }
            )
        return results

    # ------------------------------------------------------------------
    # Public API – find similar players
    # ------------------------------------------------------------------
    def find_similar_players(self, player_id: str, season: str, top_k: int = 5):
        mask = (self.df["master_player_id"] == player_id) & (
            self.df["season_id"] == season
        )
        if not mask.any():
            raise ValueError("Player/Season combination not found.")

        q_idx = self.df[mask].index[0]
        q_row = self.df.loc[q_idx]
        q_coverage = float(self._row_coverage.loc[q_idx])
        q_tier = _classify_coverage(q_coverage)

        if q_tier == "insufficient_data":
            raise ValueError(
                f"Insufficient feature coverage ({q_coverage*100:.1f}%) "
                f"for reliable similarity comparison. "
                f"At least 40% feature coverage is required."
            )

        pos = q_row["position"]

        # Filter to same position, exclude the query row itself
        pool_mask = (self.df["position"] == pos) & ~(
            (self.df["master_player_id"] == player_id)
            & (self.df["season_id"] == season)
        )
        pool_indices = self.df[pool_mask].index.tolist()

        if not pool_indices:
            return []

        pair_results = self._pairwise_aware_similarity(q_idx, pool_indices)

        # Filter out insufficient_data candidates
        usable = [r for r in pair_results if r["data_quality"] != "insufficient_data"]

        # Sort descending by similarity
        usable.sort(key=lambda r: r["similarity_score"], reverse=True)
        top = usable[:top_k]

        results = []
        for r in top:
            row = self.df.loc[r["index"]]
            results.append(
                {
                    "Queried Player": q_row["canonical_name"],
                    "Queried Season": q_row["season_id"],
                    "Comparable Player": row["canonical_name"],
                    "Comparable Player ID": row["master_player_id"],
                    "Comparable Season": row["season_id"],
                    "Similarity Score": r["similarity_score"],
                    "Position Compatibility": f"{pos} <-> {row['position']}",
                    "Feature Coverage": f"{r['feature_coverage']*100:.1f}%",
                    "Shared Features": r["shared_features"],
                    "Data Quality": r["data_quality"],
                    "Confidence": r["confidence"],
                    "Historical Transfer Fee (Context Only)": row["fee_gbp"],
                }
            )

        return results

    # ------------------------------------------------------------------
    # Profile comparison (hypothetical player)
    # ------------------------------------------------------------------
    def compare_profile_to_dataset(self, profile: dict, top_k: int = 5):
        pos = profile.get("position", "UNKNOWN")

        # Build a raw vector; mark missing as NaN
        q_raw = []
        valid_flags = []
        for f in self.sim_features:
            if f in profile and pd.notnull(profile[f]):
                q_raw.append(float(profile[f]))
                valid_flags.append(True)
            else:
                q_raw.append(np.nan)
                valid_flags.append(False)

        coverage = sum(valid_flags) / len(self.sim_features)
        tier = _classify_coverage(coverage)
        if tier == "insufficient_data":
            raise ValueError(
                f"Insufficient feature coverage ({coverage*100:.1f}%) "
                f"for hypothetical profile comparison."
            )

        # Fill NaN with global medians just for scaling, but track validity
        global_medians = self._raw_numeric.median().fillna(0)
        q_filled = [
            v if not np.isnan(v) else global_medians[self.sim_features[i]]
            for i, v in enumerate(q_raw)
        ]
        q_scaled = self.global_scaler.transform(
            np.array(q_filled).reshape(1, -1)
        )[0]

        # Filter pool by position
        pool_mask = self.df["position"] == pos
        pool_indices = self.df[pool_mask].index.tolist()
        if not pool_indices:
            return []

        # Pairwise with only shared valid features
        results_raw = []
        for pidx in pool_indices:
            p_valid = self._validity_mask.loc[pidx]
            shared_mask = [vf and bool(pv) for vf, pv in zip(valid_flags, p_valid)]
            shared_count = sum(shared_mask)
            if shared_count < 1:
                continue
            shared_cols_idx = [i for i, m in enumerate(shared_mask) if m]
            q_v = np.array([q_scaled[i] for i in shared_cols_idx]).reshape(1, -1)
            p_vals = self._scaled.loc[pidx]
            p_v = np.array(
                [p_vals[self.sim_features[i]] for i in shared_cols_idx]
            ).reshape(1, -1)

            q_norm = np.linalg.norm(q_v)
            p_norm = np.linalg.norm(p_v)
            if q_norm == 0 or p_norm == 0:
                sim = 0.0
            else:
                sim = float(cosine_similarity(q_v, p_v)[0][0])

            overlap = shared_count / len(self.sim_features)
            results_raw.append(
                {
                    "index": pidx,
                    "similarity_score": round(sim, 4),
                    "feature_coverage": round(overlap, 4),
                    "data_quality": _classify_coverage(overlap),
                }
            )

        results_raw.sort(key=lambda r: r["similarity_score"], reverse=True)
        top = results_raw[:top_k]

        results = []
        for r in top:
            row = self.df.loc[r["index"]]
            results.append(
                {
                    "Queried Player": "Hypothetical Profile",
                    "Queried Season": "N/A",
                    "Comparable Player": row["canonical_name"],
                    "Comparable Season": row["season_id"],
                    "Similarity Score": r["similarity_score"],
                    "Position Compatibility": f"{pos} <-> {row['position']}",
                    "Feature Coverage": f"{r['feature_coverage']*100:.1f}%",
                    "Data Quality": r["data_quality"],
                    "Historical Transfer Fee (Context Only)": row["fee_gbp"],
                }
            )
        return results

    # ------------------------------------------------------------------
    # Direct 1-v-1 comparison (used by Phase 13 tests)
    # ------------------------------------------------------------------
    def compare_players(self, p1_id, p1_season, p2_id, p2_season):
        m1 = (self.df["master_player_id"] == p1_id) & (
            self.df["season_id"] == p1_season
        )
        m2 = (self.df["master_player_id"] == p2_id) & (
            self.df["season_id"] == p2_season
        )

        if not m1.any() or not m2.any():
            raise ValueError("Player/Season not found.")

        idx1 = self.df[m1].index[0]
        idx2 = self.df[m2].index[0]

        r1 = self.df.loc[idx1]
        r2 = self.df.loc[idx2]

        if r1["position"] != r2["position"]:
            return 0.0  # Strict position compatibility constraint

        # Use the missing-data-aware path
        pair = self._pairwise_aware_similarity(idx1, [idx2])
        return pair[0]["similarity_score"]
