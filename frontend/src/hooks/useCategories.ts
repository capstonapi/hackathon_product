import { useQuery } from '@tanstack/react-query'

import { getCategories } from '../api/categories'
import { queryKeys } from './queryKeys'

export function useCategories() {
  return useQuery({ queryKey: queryKeys.categories(), queryFn: getCategories })
}
