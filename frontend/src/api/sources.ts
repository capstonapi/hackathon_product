import { apiClient } from './client'
import type { SourceCount } from '../types/source'

export async function getSources(): Promise<SourceCount[]> {
  const { data } = await apiClient.get<SourceCount[]>('/sources/')
  return data
}
