import { apiClient } from './client'
import type { ArticleSearchParams, RelatedArticle } from '../types/article'
import type { Paginated } from '../types/pagination'

export async function searchArticles(params: ArticleSearchParams): Promise<Paginated<RelatedArticle>> {
  const { data } = await apiClient.get<Paginated<RelatedArticle>>('/articles/search/', { params })
  return data
}
