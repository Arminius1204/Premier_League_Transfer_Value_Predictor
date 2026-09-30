import { fetchApi } from './client';
import * as T from './types';

export async function simulateWhatIf(playerId: string, season: string, changes: Record<string, number>): Promise<T.SimulationResponse> {
  return fetchApi<T.SimulationResponse>('/simulate', {
    method: 'POST',
    body: JSON.stringify({ player_id: playerId, season, changes }),
  });
}

export async function profileSimilarity(profile: any): Promise<{ results: T.SimilarPlayer[] }> {
  return fetchApi<{ results: T.SimilarPlayer[] }>('/similarity/profile', {
    method: 'POST',
    body: JSON.stringify(profile),
  });
}
