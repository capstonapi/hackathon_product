import { apiClient } from './client'
import type { ArticleDetail, ArticleListItem, ArticleListParams, RelatedArticle, TimelineResponse } from '../types/article'
import type { Paginated } from '../types/pagination'

export async function getArticles(params: ArticleListParams = {}): Promise<Paginated<ArticleListItem>> {
  const { data } = await apiClient.get<Paginated<ArticleListItem>>('/articles/', { params })
  return data
}

export async function getLatestArticles(params: { page?: number; page_size?: number } = {}): Promise<Paginated<ArticleListItem>> {
  const { data } = await apiClient.get<Paginated<ArticleListItem>>('/articles/latest/', { params })
  return data
}

export async function getArticle(id: number): Promise<ArticleDetail> {
  const { data } = await apiClient.get<ArticleDetail>(`/articles/${id}/`)
  return data
}

export async function getRelatedArticles(id: number): Promise<Paginated<RelatedArticle>> {
  const { data } = await apiClient.get<Paginated<RelatedArticle>>(`/articles/${id}/related/`)
  return data
}

export async function getTimeline(id: number): Promise<TimelineResponse> {
  const { data } = await apiClient.get<TimelineResponse>(`/articles/${id}/timeline/`)
  return data
}

export async function saveArticle(id: number): Promise<void> {
  await apiClient.post(`/articles/${id}/save/`)
}

export async function unsaveArticle(id: number): Promise<void> {
  await apiClient.delete(`/articles/${id}/save/`)
}
