import type { ArticleListParams, ArticleSearchParams } from '../types/article'

export const queryKeys = {
  articles: (params: ArticleListParams) => ['articles', params] as const,
  latestArticles: (params: { page?: number; page_size?: number }) => ['articles', 'latest', params] as const,
  article: (id: number) => ['articles', id] as const,
  related: (id: number) => ['articles', id, 'related'] as const,
  timeline: (id: number) => ['articles', id, 'timeline'] as const,
  search: (params: ArticleSearchParams) => ['search', params] as const,
  categories: () => ['categories'] as const,
  sources: () => ['sources'] as const,
  saved: (params: { page?: number; page_size?: number }) => ['saved', params] as const,
  history: (params: { page?: number; page_size?: number }) => ['history', params] as const,
  conversation: (id: number) => ['chat', id] as const,
}
