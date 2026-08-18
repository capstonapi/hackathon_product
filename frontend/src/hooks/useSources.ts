import { useQuery } from '@tanstack/react-query'

import { getSources } from '../api/sources'
import { queryKeys } from './queryKeys'

export function useSources() {
  return useQuery({ queryKey: queryKeys.sources(), queryFn: getSources })
}
