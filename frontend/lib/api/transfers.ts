import { fetchApi } from './client';
import * as T from './types';

export async function getTransfers(params: Record<string, any> = {}): Promise<T.TransferResponse> {
  const searchParams = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, value.toString());
    }
  }
  return fetchApi<T.TransferResponse>(`/transfers?${searchParams.toString()}`);
}
