import { useQuery } from '@tanstack/react-query'
import { fetchAssets } from '../api/assets'

export function useAssets(tags?: string[]) {
  return useQuery({
    queryKey: ['assets', tags],
    queryFn: () => fetchAssets(tags),
    staleTime: 5 * 60 * 1000,
    refetchInterval: 10 * 60 * 1000,
  })
}
