import client from "./client";

export async function fetchRebalanceConfigs() {
  const { data } = await client.get("/rebalance/configs");
  return data;
}

export async function saveRebalanceConfig(config: {
  asset_id: string;
  ticker: string;
  target_weight_pct: number;
  min_weight_pct: number;
  max_weight_pct: number;
  rebalance_threshold_pct?: number;
  correction_days?: number;
}) {
  const { data } = await client.post("/rebalance/configs", config);
  return data;
}

export async function generateRebalancePlan() {
  const { data } = await client.post("/rebalance/plan");
  return data;
}
