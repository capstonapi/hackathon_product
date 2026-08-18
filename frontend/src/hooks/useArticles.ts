import { keepPreviousData, useQuery } from '@tanstack/react-query'

import { getArticle, getArticles, getLatestArticles, getRelatedArticles, getTimeline } from '../api/articles'
import type { ArticleListParams } from '../types/article'
import { queryKeys } from './queryKeys'

export function useArticles(params: ArticleListParams) {
  return useQuery({
    queryKey: queryKeys.articles(params),
    queryFn: () => getArticles(params),
    placeholderData: keepPreviousData,
  })
}

export function useLatestArticles(params: { page?: number; page_size?: number } = {}) {
  return useQuery({
    queryKey: queryKeys.latestArticles(params),
    queryFn: () => getLatestArticles(params),
    placeholderData: keepPreviousData,
  })
}

export function useArticle(id: number) {
  return useQuery({
    queryKey: queryKeys.article(id),
    queryFn: () => getArticle(id),
    enabled: Number.isFinite(id),
  })
}

export function useRelatedArticles(id: number) {
  return useQuery({
    queryKey: queryKeys.related(id),
    queryFn: () => getRelatedArticles(id),
    enabled: Number.isFinite(id),
  })
}

export function useTimeline(id: number) {
  return useQuery({
    queryKey: queryKeys.timeline(id),
    queryFn: () => getTimeline(id),
    enabled: Number.isFinite(id),
  })
}
