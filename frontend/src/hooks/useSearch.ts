import { keepPreviousData, useQuery } from '@tanstack/react-query'

import { searchArticles } from '../api/search'
import type { ArticleSearchParams } from '../types/article'
import { queryKeys } from './queryKeys'

export function useSearchArticles(params: ArticleSearchParams) {
  return useQuery({
    queryKey: queryKeys.search(params),
    queryFn: () => searchArticles(params),
    enabled: params.q.trim().length > 0,
    placeholderData: keepPreviousData,
  })
}
