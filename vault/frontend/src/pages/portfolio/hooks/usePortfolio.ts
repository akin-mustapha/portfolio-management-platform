import { useQuery } from "@tanstack/react-query";
import {
  fetchPortfolioSummary,
  fetchPortfolioHistory,
} from "../../../api/portfolio";
import {
  presentPortfolioSummary,
  portfolioValueSeries,
  portfolioPnlSeries,
  portfolioDrawdown,
  type RawPortfolioSummary,
  type RawPortfolioHistoryRow,
} from "../../../presenters/portfolioPresenter";

export function usePortfolioSummary() {
  return useQuery({
    queryKey: ["portfolio", "summary"],
    queryFn: async () =>
      presentPortfolioSummary(
        (await fetchPortfolioSummary()) as RawPortfolioSummary,
      ),
    staleTime: 5 * 60 * 1000,
    refetchInterval: 10 * 60 * 1000,
  });
}

export interface PortfolioHistoryVM {
  value_series: ReturnType<typeof portfolioValueSeries>;
  pnl_series: ReturnType<typeof portfolioPnlSeries>;
  drawdown: ReturnType<typeof portfolioDrawdown>;
}

export function usePortfolioHistory(from?: string, to?: string) {
  return useQuery({
    queryKey: ["portfolio", "history", from, to],
    queryFn: async (): Promise<PortfolioHistoryVM> => {
      const rows = (await fetchPortfolioHistory(
        from,
        to,
      )) as RawPortfolioHistoryRow[];
      return {
        value_series: portfolioValueSeries(rows),
        pnl_series: portfolioPnlSeries(rows),
        drawdown: portfolioDrawdown(rows),
      };
    },
    staleTime: 5 * 60 * 1000,
  });
}
