import { fetchApi } from './client';
import * as T from './types';

export async function getMarketAnalysis(season?: string, position?: string): Promise<T.MarketAnalysisResponse> {
  const params = new URLSearchParams();
  if (season) params.append('season', season);
  if (position) params.append('position', position);
  return fetchApi<T.MarketAnalysisResponse>(`/market-analysis?${params.toString()}`);
}

export async function getModelMetadata(): Promise<T.ModelMetadataResponse> {
  return fetchApi<T.ModelMetadataResponse>('/models');
}
