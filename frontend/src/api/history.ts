import { apiClient } from './client'
import type { ConversationSummary } from '../types/chat'
import type { Paginated } from '../types/pagination'

export async function getHistory(params: { page?: number; page_size?: number } = {}): Promise<Paginated<ConversationSummary>> {
  const { data } = await apiClient.get<Paginated<ConversationSummary>>('/history/', { params })
  return data
}
