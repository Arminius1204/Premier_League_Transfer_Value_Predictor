export interface Pagination {
  total: number;
  limit: number;
  offset: number;
}

export interface TransferRecord {
  season_id?: string | null;
  transfer_type?: string | null;
  fee_gbp?: number | null;
  buyer_club?: string | null;
  seller_club?: string | null;
  player_id?: string | null;
  player_name?: string | null;
}

export interface PlayerSearchItem {
  player_id: string;
  player_name: string;
  position: string;
}

export interface PlayerSearchResponse extends Pagination {
  items: PlayerSearchItem[];
}

export interface PlayerDetail {
  player_id: string;
  player_name: string;
  position: string;
  seasons: string[];
  clubs: string[];
  transfer_history: TransferRecord[];
}

export interface ValuationResponse {
  player_id: string;
  player_name: string;
  prediction: number;
  lower_bound: number;
  upper_bound: number;
  currency: string;
  model: string;
  uncertainty_method: string;
  feature_coverage?: number | null;
}

export interface ExplanationContributor {
  feature: string;
  impact: string;
}

export interface ExplanationResponse {
  player_id: string;
  prediction: number;
  positive_contributors: ExplanationContributor[];
  negative_contributors: ExplanationContributor[];
  method: string;
}

export interface SimilarPlayer {
  player_id: string;
  player_name: string;
  season: string;
  similarity_score: number;
  position: string;
  feature_coverage: number;
  historical_transfer_fee?: number | null;
}

export interface SimilarityResponse {
  player: {
    player_id: string;
    season: string;
  };
  results: SimilarPlayer[];
}

export interface SimulationBounds {
  prediction: number;
  lower_bound: number;
  upper_bound: number;
}

export interface SimulationResponse {
  player_id: string;
  baseline: SimulationBounds;
  scenario: SimulationBounds;
  absolute_change: number;
  percentage_change: number;
  changed_features: Record<string, number>;
  warnings: string[];
}

export interface MarketAnalysisResponse {
  total_transfers: number;
  disclosed_transfers: number;
  median_fee: number;
  mean_fee: number;
}

export interface TransferResponse extends Pagination {
  items: TransferRecord[];
}

export interface ModelMetadataResponse {
  production_model: string;
  candidate_models: string[];
  ensemble_information: {
    weights: Record<string, number>;
    method: string;
  };
  validation_methodology: string;
  metrics: {
    MAE: number;
    RMSE: number;
    R2: number;
    median_absolute_error: number;
  };
  uncertainty_methodology: string;
  training_period: string;
  final_holdout_period: string;
}
