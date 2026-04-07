import { useQuery } from '@tanstack/react-query'
import { fetchPortfolioSummary, fetchPortfolioHistory } from '../api/portfolio'

export function usePortfolioSummary() {
  return useQuery({
    queryKey: ['portfolio', 'summary'],
    queryFn: fetchPortfolioSummary,
    staleTime: 5 * 60 * 1000, // 5 min
    refetchInterval: 10 * 60 * 1000, // background refresh every 10 min
  })
}

export function usePortfolioHistory(from?: string, to?: string) {
  return useQuery({
    queryKey: ['portfolio', 'history', from, to],
    queryFn: () => fetchPortfolioHistory(from, to),
    staleTime: 5 * 60 * 1000,
  })
}
