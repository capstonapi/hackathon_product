import { keepPreviousData, useQuery } from '@tanstack/react-query'

import { getHistory } from '../api/history'
import { queryKeys } from './queryKeys'

export function useHistory(params: { page?: number; page_size?: number } = {}) {
  return useQuery({
    queryKey: queryKeys.history(params),
    queryFn: () => getHistory(params),
    placeholderData: keepPreviousData,
  })
}
