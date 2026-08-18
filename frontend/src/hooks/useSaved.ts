import { keepPreviousData, useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { getSavedArticles } from '../api/saved'
import { saveArticle, unsaveArticle } from '../api/articles'
import { queryKeys } from './queryKeys'

export function useSavedArticles(params: { page?: number; page_size?: number } = {}) {
  return useQuery({
    queryKey: queryKeys.saved(params),
    queryFn: () => getSavedArticles(params),
    placeholderData: keepPreviousData,
  })
}

/** Best-effort "is this article in the user's saved list" check against the first page of saves. */
export function useIsArticleSaved(articleId: number) {
  const { data, isLoading } = useSavedArticles({ page_size: 100 })
  return { isSaved: Boolean(data?.results.some((article) => article.id === articleId)), isLoading }
}

export function useSaveArticle() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (articleId: number) => saveArticle(articleId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['saved'] }),
  })
}

export function useUnsaveArticle() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (articleId: number) => unsaveArticle(articleId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['saved'] }),
  })
}
