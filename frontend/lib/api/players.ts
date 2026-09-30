import { fetchApi } from './client';
import * as T from './types';

export async function searchPlayers(q?: string, season?: string, position?: string, limit: number = 20, offset: number = 0): Promise<T.PlayerSearchResponse> {
  const params = new URLSearchParams();
  if (q) params.append('q', q);
  if (season) params.append('season', season);
  if (position) params.append('position', position);
  params.append('limit', limit.toString());
  params.append('offset', offset.toString());
  
  return fetchApi<T.PlayerSearchResponse>(`/players?${params.toString()}`);
}

export async function getPlayerDetail(id: string): Promise<T.PlayerDetail> {
  return fetchApi<T.PlayerDetail>(`/players/${id}`);
}

export async function getPlayerValuation(id: string, season?: string): Promise<T.ValuationResponse> {
  const params = new URLSearchParams();
  if (season) params.append('season', season);
  return fetchApi<T.ValuationResponse>(`/players/${id}/valuation?${params.toString()}`);
}

export async function getPlayerExplanation(id: string, season?: string): Promise<T.ExplanationResponse> {
  const params = new URLSearchParams();
  if (season) params.append('season', season);
  return fetchApi<T.ExplanationResponse>(`/players/${id}/explanation?${params.toString()}`);
}

export async function getSimilarPlayers(id: string, season: string, top_k: number = 5): Promise<T.SimilarityResponse> {
  const params = new URLSearchParams({ season, top_k: top_k.toString() });
  return fetchApi<T.SimilarityResponse>(`/players/${id}/similar?${params.toString()}`);
}
