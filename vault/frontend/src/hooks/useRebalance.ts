import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  fetchRebalanceConfigs,
  saveRebalanceConfig,
  generateRebalancePlan,
} from "../api/rebalance";
import {
  presentRebalanceConfigs,
  presentRebalancePlanResult,
  type RebalanceConfigVM,
  type RebalancePlanResultVM,
} from "../presenters/rebalancePresenter";

export type { RebalanceConfigVM, RebalancePlanResultVM };

export function useRebalanceConfigs() {
  return useQuery({
    queryKey: ["rebalance", "configs"],
    queryFn: async (): Promise<RebalanceConfigVM[]> =>
      presentRebalanceConfigs((await fetchRebalanceConfigs()) as unknown[]),
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
  return useMutation({
    mutationFn: async (): Promise<RebalancePlanResultVM> =>
      presentRebalancePlanResult(await generateRebalancePlan()),
  });
}
