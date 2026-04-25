// ---- Raw API shapes ----

export interface RawAssetHistoryResponse {
  asset_price?: {
    dates: string[]
    values: (number | null)[]
    price_ma_20d?: (number | null)[]
    price_ma_50d?: (number | null)[]
  }
  asset_value?: {
    dates: string[]
    values: (number | null)[]
  }
  asset_profit_range?: {
    dates: string[]
    values: (number | null)[]
    high_30d?: (number | null)[]
    low_30d?: (number | null)[]
  }
  asset_return?: {
    dates: string[]
    values: (number | null)[]
  }
  [key: string]: unknown
}

export interface RawAssetProfileResponse {
  ticker?: string
  name?: string
  tags?: string[]
  [key: string]: unknown
}

// ---- View models ----

export interface AssetPriceSeriesVM {
  dates: string[]
  values: (number | null)[]
  price_ma_20d: (number | null)[]
  price_ma_50d: (number | null)[]
}

export interface AssetValueSeriesVM {
  dates: string[]
  values: (number | null)[]
}

export interface AssetPnlSeriesVM {
  dates: string[]
  values: (number | null)[]
  high_30d: (number | null)[]
  low_30d: (number | null)[]
}

export interface AssetReturnSeriesVM {
  dates: string[]
  /** Already multiplied by 100 — ready to render as % */
  values: (number | null)[]
}

export interface AssetHistoryVM {
  asset_price: AssetPriceSeriesVM
  asset_value: AssetValueSeriesVM
  asset_profit_range: AssetPnlSeriesVM
  asset_return: AssetReturnSeriesVM
}

export type KpiColorCode = 'positive' | 'negative' | 'neutral'

export interface AssetKpiItem {
  label: string
  value: number | undefined
  suffix?: string
  colorCode?: KpiColorCode
  metricKey?: string
}

export interface AssetKpiGroupsVM {
  performance: AssetKpiItem[]
  risk: AssetKpiItem[]
  allocation: AssetKpiItem[]
}

export interface AssetTableRow {
  ticker: string
  name: string
  price_series: (number | null)[]
  /** Sentiment derived from price_series — used by sparkline */
  sparklineSentiment: 'positive' | 'negative' | 'neutral'
  [key: string]: unknown
}

// ---- Number formatting helpers (pure, no hooks) ----

export function fmtNum(v: unknown, decimals = 2): string {
  if (v == null) return '—'
  return Number(v).toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })
}

export function fmtPct(v: unknown): string {
  if (v == null) return '—'
  return `${Number(v).toFixed(2)}%`
}

// ---- Presenter functions ----

function colorCode(value: number | undefined): KpiColorCode {
  if (value == null) return 'neutral'
  return value >= 0 ? 'positive' : 'negative'
}

export function presentAssetKpis(assetRow: Record<string, unknown>): AssetKpiGroupsVM {
  const profit = assetRow.profit as number | undefined
  const pnlPct = assetRow.pnl_pct as number | undefined

  return {
    performance: [
      { label: 'Value', value: assetRow.value as number | undefined },
      { label: 'P&L', value: profit, colorCode: colorCode(profit), metricKey: 'profit' },
      { label: 'P&L %', value: pnlPct, suffix: '%', colorCode: colorCode(pnlPct), metricKey: 'pnl_pct' },
    ],
    risk: [
      { label: 'Vol 30d', value: assetRow.volatility_30d as number | undefined, metricKey: 'volatility_30d' },
      { label: 'VaR 95%', value: assetRow.var_95_1d as number | undefined, metricKey: 'var_95_1d' },
      { label: 'Beta 60d', value: assetRow.beta_60d as number | undefined },
    ],
    allocation: [
      { label: 'Weight', value: assetRow.weight_pct as number | undefined, suffix: '%', metricKey: 'weight_pct' },
      { label: 'Avg Price', value: assetRow.avg_price as number | undefined, metricKey: 'avg_price' },
      { label: 'Cost', value: assetRow.cost as number | undefined },
    ],
  }
}

export function sparklineSentiment(
  priceSeries: (number | null)[] | undefined,
): 'positive' | 'negative' | 'neutral' {
  const vals = (priceSeries ?? []).filter((v): v is number => v != null)
  if (vals.length < 2) return 'neutral'
  return vals[vals.length - 1] >= vals[0] ? 'positive' : 'negative'
}

export function presentAssetHistory(raw: RawAssetHistoryResponse): AssetHistoryVM {
  const rawReturn = raw.asset_return
  return {
    asset_price: {
      dates: raw.asset_price?.dates ?? [],
      values: raw.asset_price?.values ?? [],
      price_ma_20d: raw.asset_price?.price_ma_20d ?? [],
      price_ma_50d: raw.asset_price?.price_ma_50d ?? [],
    },
    asset_value: {
      dates: raw.asset_value?.dates ?? [],
      values: raw.asset_value?.values ?? [],
    },
    asset_profit_range: {
      dates: raw.asset_profit_range?.dates ?? [],
      values: raw.asset_profit_range?.values ?? [],
      high_30d: raw.asset_profit_range?.high_30d ?? [],
      low_30d: raw.asset_profit_range?.low_30d ?? [],
    },
    asset_return: {
      dates: rawReturn?.dates ?? [],
      values: (rawReturn?.values ?? []).map((v) => (v != null ? Number(v) * 100 : null)),
    },
  }
}
