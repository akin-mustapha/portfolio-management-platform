// ---- Raw API shapes ----

export interface RawRebalanceConfig {
  asset_id: string
  ticker: string
  target_weight_pct: number
  min_weight_pct: number
  max_weight_pct: number
  rebalance_threshold_pct?: number
  correction_days?: number
  [key: string]: unknown
}

export interface RawRebalancePlanResult {
  status: string
  [key: string]: unknown
}

// ---- View models ----

export interface RebalanceConfigVM {
  asset_id: string
  ticker: string
  target_weight_pct: number
  min_weight_pct: number
  max_weight_pct: number
  rebalance_threshold_pct: number
  correction_days: number
}

export interface RebalancePlanResultVM {
  message: string
  noDrift: boolean
}

// ---- Presenter functions ----

export function presentRebalanceConfigs(raw: unknown[]): RebalanceConfigVM[] {
  return (raw as RawRebalanceConfig[]).map((c) => ({
    asset_id: c.asset_id,
    ticker: c.ticker,
    target_weight_pct: c.target_weight_pct,
    min_weight_pct: c.min_weight_pct,
    max_weight_pct: c.max_weight_pct,
    rebalance_threshold_pct: c.rebalance_threshold_pct ?? 0,
    correction_days: c.correction_days ?? 0,
  }))
}

export function presentRebalancePlanResult(raw: RawRebalancePlanResult): RebalancePlanResultVM {
  const noDrift = raw.status === 'no_drift'
  return {
    noDrift,
    message: noDrift
      ? 'All assets within threshold — no plan needed.'
      : 'Rebalancing plan generated.',
  }
}
