import { useQuery } from "@tanstack/react-query";
import { fetchAssetHistory, fetchAssetProfile } from "../api/assets";

export function useAssetHistory(
  ticker: string | null,
  from?: string,
  to?: string,
) {
  return useQuery({
    queryKey: ["asset", "history", ticker, from, to],
    queryFn: () => fetchAssetHistory(ticker!, from, to),
    enabled: !!ticker,
    staleTime: 5 * 60 * 1000,
  });
}

export function useAssetProfile(ticker: string | null) {
  return useQuery({
    queryKey: ["asset", "profile", ticker],
    queryFn: () => fetchAssetProfile(ticker!),
    enabled: !!ticker,
    staleTime: 5 * 60 * 1000,
  });
}
