import { useQuery } from '@tanstack/react-query'
import { fetchPortfolioSummary, fetchPortfolioHistory } from '../api/portfolio'
import { presentPortfolioSummary, type RawPortfolioSummary } from '../presenters/portfolioPresenter'

export function usePortfolioSummary() {
  return useQuery({
    queryKey: ['portfolio', 'summary'],
    queryFn: async () => presentPortfolioSummary(await fetchPortfolioSummary() as RawPortfolioSummary),
    staleTime: 5 * 60 * 1000,
    refetchInterval: 10 * 60 * 1000,
  })
}

export function usePortfolioHistory(from?: string, to?: string) {
  return useQuery({
    queryKey: ['portfolio', 'history', from, to],
    queryFn: () => fetchPortfolioHistory(from, to),
    staleTime: 5 * 60 * 1000,
  })
}
