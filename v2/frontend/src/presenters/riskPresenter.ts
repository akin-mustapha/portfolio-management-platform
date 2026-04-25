// ---- View models ----

export interface ProfitabilityVM {
  profitable: number
  unprofitable: number
  data: Array<{ name: string; value: number }>
}

export interface UnprofitablePnlPoint {
  date: string
  value: number
}

// ---- Presenter functions ----

export function presentProfitability(
  assets: Array<{ ticker: string; profit: number }>,
): ProfitabilityVM {
  const profitable = assets.filter((a) => (a.profit ?? 0) > 0).length
  const unprofitable = assets.length - profitable
  return {
    profitable,
    unprofitable,
    data: [
      { name: 'Profitable', value: profitable },
      { name: 'Unprofitable', value: unprofitable },
    ],
  }
}

export function presentUnprofitablePnl(
  losers_pnl: Record<string, number>,
): UnprofitablePnlPoint[] {
  return Object.entries(losers_pnl)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, value]) => ({ date, value }))
}
