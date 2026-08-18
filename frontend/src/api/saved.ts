import { apiClient } from './client'
import type { ArticleListItem } from '../types/article'
import type { Paginated } from '../types/pagination'

export async function getSavedArticles(params: { page?: number; page_size?: number } = {}): Promise<Paginated<ArticleListItem>> {
  const { data } = await apiClient.get<Paginated<ArticleListItem>>('/saved/', { params })
  return data
}
