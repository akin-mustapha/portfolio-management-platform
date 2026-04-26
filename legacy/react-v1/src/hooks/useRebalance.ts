import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  fetchRebalanceConfigs,
  saveRebalanceConfig,
  generateRebalancePlan,
} from "../api/rebalance";

export function useRebalanceConfigs() {
  return useQuery({
    queryKey: ["rebalance", "configs"],
    queryFn: fetchRebalanceConfigs,
    staleTime: 60 * 1000,
  });
}

export function useSaveRebalanceConfig() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: saveRebalanceConfig,
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ["rebalance", "configs"] }),
  });
}

export function useGenerateRebalancePlan() {
  return useMutation({ mutationFn: generateRebalancePlan });
}
