const CURRENCY_SYMBOLS: Record<string, string> = { EUR: '€', USD: '$', GBP: '£' }

// ---- Raw API shape ----

export interface RawAsset {
  ticker: string
  name: string
  weight_pct: number | null
  profit: number | null
  value: number | null
  pnl_pct: number | null
  var_95_1d: number | null
  daily_value_return: number | null
  value_ma_crossover_signal: number | null
  price_series: number[]
  tags: string[]
  trend?: string
  [key: string]: unknown
}

export interface RawPortfolioHistoryRow {
  data_date: string
  investments_total_cost: number
  investments_unrealized_pnl: number
  investments_realized_pnl: number
  total_value: number
  daily_value_change_pct: number | null
  fx_impact_total: number | null
  [key: string]: unknown
}

export interface RawSnapshot {
  currency?: string
  total_value?: number
  investments_realized_pnl?: number
  investments_unrealized_pnl?: number
  investments_total_cost?: number
  cash_available_to_trade?: number
  cash_reserved_for_orders?: number
  cash_in_pies?: number
  daily_value_change_pct?: number | null
  portfolio_volatility_weighted?: number | null
  portfolio_beta_weighted?: number | null
  sharpe_ratio_30d?: number | null
  benchmark_return_daily?: number | null
  portfolio_vs_benchmark_30d?: number | null
}

export interface RawAssetHistoryRow {
  ticker: string
  profit: number
  data_date: string
  is_profitable: 0 | 1
  [key: string]: unknown
}

export interface RawPortfolioSummary {
  assets: RawAsset[]
  assets_history: RawAssetHistoryRow[]
  portfolio_history: RawPortfolioHistoryRow[]
  portfolio_current_snapshot: RawSnapshot
  available_tags: string[]
}

// ---- View models ----

export interface KpiVM {
  value: number
  currency: string
  currency_symbol: string
  realized_pnl: number
  unrealized_pnl: number
  total_cost: number
  cash: number
  cash_reserved: number
  cash_in_pies: number
  daily_value_change_pct: number | null
  portfolio_vol: number | null
  portfolio_beta: number | null
  sharpe_ratio_30d: number | null
  benchmark_return_daily: number | null
  portfolio_vs_benchmark_30d: number | null
  daily_change_series: { dates: string[]; values: (number | null)[] }
}

export interface PortfolioValueSeriesVM {
  dates: string[]
  values: number[]
  costs: number[]
}

export interface PortfolioPnlSeriesVM {
  dates: string[]
  values: number[]
  realized: number[]
  total_pnl: number[]
}

export interface PortfolioDrawdownVM {
  dates: string[]
  drawdown_pct: number[]
}

export interface AssetTableVM {
  fields: string[]
  rows: RawAsset[]
}

export interface PortfolioValueChartRow {
  date: string
  cost: number
  pnl: number
  value: number
  realized: number | null
  totalPnl: number | null
}

export interface PortfolioPnlChartRow {
  date: string
  unrealized: number
  realized: number
  total: number
}

export interface PositionWeightTop10Item {
  ticker: string
  weight_pct: number
  profit: number
  value: number
  name: string
}

export interface PositionDistributionItem {
  ticker: string
  weight_pct: number
  roi_pct: number
  profit: number
  value: number
  name: string
}

export interface PositionWeightSeriesVM {
  series: { ticker: string; weight_pct: number; breakdown: string }[]
  avg_weight_pct: number
}

export interface WinnerLoserItem {
  ticker: string
  weight_pct: number
  profit: number
  value: number
  name: string
  label: string
}

export interface DailyMoverItem {
  ticker: string
  daily_value_return: number
  label: string
  name: string
  /** Pre-formatted for display, e.g. "+1.23%" */
  formattedReturn: string
}

export interface VarItem {
  ticker: string
  var_95_1d: number
  label: string
  name: string
}

export interface PortfolioSummaryVM {
  kpi: KpiVM
  asset_table: AssetTableVM
  portfolio_value_series: PortfolioValueSeriesVM
  portfolio_pnl_series: PortfolioPnlSeriesVM
  portfolio_drawdown: PortfolioDrawdownVM
  position_weight_series: PositionWeightSeriesVM
  position_distribution: PositionDistributionItem[]
  winners: WinnerLoserItem[]
  losers: WinnerLoserItem[]
  daily_movers: DailyMoverItem[]
  var_by_position: VarItem[]
  portfolio_fx_attribution: { fx_impact_total: number; unrealized_pnl: number }
  profitability: Array<{ ticker: string; profit: number }>
  /** Pre-merged rows for PortfolioValueChart — pnl derived here, not in component */
  portfolio_value_chart_rows: PortfolioValueChartRow[]
  /** Pre-merged rows for PortfolioPnlChart */
  portfolio_pnl_chart_rows: PortfolioPnlChartRow[]
  /** Top-10 by weight, pre-sorted, for PositionWeightChart */
  position_weight_top10: PositionWeightTop10Item[]
  /** Summed profit of losing positions, sorted by date, for UnprofitablePnlChart */
  losers_pnl: Array<{ date: string; value: number }>
  available_tags: string[]
}

// ---- Presenter ----

function round(v: number, dp: number): number {
  const factor = Math.pow(10, dp)
  return Math.round(v * factor) / factor
}

function toFloat(v: unknown): number {
  return parseFloat(String(v ?? 0)) || 0
}

function dailyChangeSeries(history: RawPortfolioHistoryRow[]) {
  const rows = history.filter((r) => r.daily_value_change_pct != null).slice(-30)
  return {
    dates: rows.map((r) => String(r.data_date)),
    values: rows.map((r) => r.daily_value_change_pct),
  }
}

function kpi(snapshot: RawSnapshot, history: RawPortfolioHistoryRow[]): KpiVM {
  const currency = snapshot.currency ?? ''
  return {
    value: snapshot.total_value ?? 0,
    currency,
    currency_symbol: CURRENCY_SYMBOLS[currency] ?? '#',
    realized_pnl: snapshot.investments_realized_pnl ?? 0,
    unrealized_pnl: snapshot.investments_unrealized_pnl ?? 0,
    total_cost: snapshot.investments_total_cost ?? 0,
    cash: snapshot.cash_available_to_trade ?? 0,
    cash_reserved: snapshot.cash_reserved_for_orders ?? 0,
    cash_in_pies: snapshot.cash_in_pies ?? 0,
    daily_value_change_pct:
      snapshot.daily_value_change_pct != null ? round(snapshot.daily_value_change_pct, 2) : null,
    portfolio_vol:
      snapshot.portfolio_volatility_weighted != null
        ? round(snapshot.portfolio_volatility_weighted, 2)
        : null,
    portfolio_beta:
      snapshot.portfolio_beta_weighted != null
        ? round(toFloat(snapshot.portfolio_beta_weighted), 2)
        : null,
    sharpe_ratio_30d:
      snapshot.sharpe_ratio_30d != null ? round(snapshot.sharpe_ratio_30d, 2) : null,
    benchmark_return_daily:
      snapshot.benchmark_return_daily != null
        ? round(toFloat(snapshot.benchmark_return_daily) * 100, 3)
        : null,
    portfolio_vs_benchmark_30d:
      snapshot.portfolio_vs_benchmark_30d != null
        ? round(toFloat(snapshot.portfolio_vs_benchmark_30d) * 100, 2)
        : null,
    daily_change_series: dailyChangeSeries(history),
  }
}

function assetTable(assets: RawAsset[]): AssetTableVM {
  if (!assets.length) return { fields: [], rows: [] }
  return { fields: Object.keys(assets[0]), rows: assets }
}

export function portfolioValueSeries(rows: RawPortfolioHistoryRow[]): PortfolioValueSeriesVM {
  return {
    dates: rows.map((r) => String(r.data_date)),
    values: rows.map((r) => toFloat(r.investments_total_cost) + toFloat(r.investments_unrealized_pnl)),
    costs: rows.map((r) => toFloat(r.investments_total_cost)),
  }
}

export function portfolioPnlSeries(rows: RawPortfolioHistoryRow[]): PortfolioPnlSeriesVM {
  return {
    dates: rows.map((r) => String(r.data_date)),
    values: rows.map((r) => toFloat(r.investments_unrealized_pnl)),
    realized: rows.map((r) => toFloat(r.investments_realized_pnl)),
    total_pnl: rows.map(
      (r) => toFloat(r.investments_unrealized_pnl) + toFloat(r.investments_realized_pnl),
    ),
  }
}

export function portfolioDrawdown(rows: RawPortfolioHistoryRow[]): PortfolioDrawdownVM {
  const dates = rows.map((r) => String(r.data_date))
  let peak = 0
  const drawdown_pct = rows.map((r) => {
    const v = toFloat(r.total_value)
    if (v > peak) peak = v
    return peak > 0 ? round(((v - peak) / peak) * 100, 4) : 0
  })
  return { dates, drawdown_pct }
}

function portfolioFxAttribution(rows: RawPortfolioHistoryRow[]) {
  if (!rows.length) return { fx_impact_total: 0, unrealized_pnl: 0 }
  const latest = rows[rows.length - 1]
  return {
    fx_impact_total: toFloat(latest.fx_impact_total),
    unrealized_pnl: toFloat(latest.investments_unrealized_pnl),
  }
}

function positionWeightSeries(assets: RawAsset[]): PositionWeightSeriesVM {
  const items = [...assets]
    .map((a) => ({ ticker: a.ticker, weight_pct: toFloat(a.weight_pct) }))
    .sort((a, b) => b.weight_pct - a.weight_pct)

  const avg_weight_pct = items.length
    ? round(items.reduce((s, i) => s + i.weight_pct, 0) / items.length, 1)
    : 0

  const top = items.slice(0, 14).map((i) => ({ ...i, breakdown: '' }))
  const rest = items.slice(14)
  const restTotal = rest.reduce((s, i) => s + i.weight_pct, 0)
  if (restTotal > 0) {
    const breakdown = rest.map((i) => `${i.ticker}: ${round(i.weight_pct, 1)}%`).join('\n')
    top.push({ ticker: 'Other', weight_pct: restTotal, breakdown })
  }
  top.sort((a, b) => a.weight_pct - b.weight_pct)
  return { series: top, avg_weight_pct }
}

function positionDistribution(assets: RawAsset[]): PositionDistributionItem[] {
  return [...assets]
    .map((a) => ({
      ticker: a.ticker,
      weight_pct: toFloat(a.weight_pct),
      roi_pct: round(toFloat(a.pnl_pct), 2),
      profit: toFloat(a.profit),
      value: toFloat(a.value),
      name: a.name,
    }))
    .sort((a, b) => b.weight_pct - a.weight_pct)
}

function roiLabel(a: RawAsset): string {
  const roi = round(toFloat(a.pnl_pct), 2)
  return `${a.ticker} ${roi >= 0 ? '+' : ''}${roi}%`
}

function topWinners(assets: RawAsset[], sortBy: 'profit' | 'weight_pct' = 'profit'): WinnerLoserItem[] {
  return [...assets]
    .map((a) => ({
      ticker: a.ticker,
      weight_pct: toFloat(a.weight_pct),
      profit: toFloat(a.profit),
      value: toFloat(a.value),
      name: a.name,
      label: roiLabel(a),
    }))
    .sort((a, b) => b[sortBy] - a[sortBy])
    .slice(0, 10)
}

function topLosers(assets: RawAsset[], sortBy: 'profit' | 'weight_pct' = 'profit'): WinnerLoserItem[] {
  return [...assets]
    .map((a) => ({
      ticker: a.ticker,
      weight_pct: toFloat(a.weight_pct),
      profit: toFloat(a.profit),
      value: toFloat(a.value),
      name: a.name,
      label: roiLabel(a),
    }))
    .sort((a, b) => a[sortBy] - b[sortBy])
    .slice(0, 10)
}

function dailyMovers(assets: RawAsset[]): DailyMoverItem[] {
  const items: DailyMoverItem[] = []
  for (const a of assets) {
    const series = a.price_series ?? []
    let daily_value_return: number
    if (series.length >= 2 && series[series.length - 2] !== 0) {
      daily_value_return =
        ((series[series.length - 1] - series[series.length - 2]) / series[series.length - 2]) * 100
    } else if (a.daily_value_return != null) {
      daily_value_return = a.daily_value_return * 100
    } else {
      continue
    }
    const sign = daily_value_return >= 0 ? '+' : ''
    items.push({
      ticker: a.ticker,
      daily_value_return,
      label: a.ticker,
      name: a.name,
      formattedReturn: `${sign}${daily_value_return.toFixed(2)}%`,
    })
  }
  return items.sort((a, b) => Math.abs(b.daily_value_return) - Math.abs(a.daily_value_return)).slice(0, 15)
}

function profitability(assets: RawAsset[]): Array<{ ticker: string; profit: number }> {
  return assets.map((a) => ({ ticker: a.ticker, profit: toFloat(a.profit) }))
}

function losersPnl(history: RawAssetHistoryRow[]): Array<{ date: string; value: number }> {
  const byDate: Record<string, number> = {}
  for (const row of history) {
    if (row.is_profitable === 0) {
      const date = String(row.data_date)
      byDate[date] = (byDate[date] ?? 0) + toFloat(row.profit)
    }
  }
  return Object.entries(byDate)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, value]) => ({ date, value }))
}

function varByPosition(assets: RawAsset[]): VarItem[] {
  return assets
    .filter((a) => a.var_95_1d != null)
    .map((a) => ({ ticker: a.ticker, var_95_1d: toFloat(a.var_95_1d), label: a.ticker, name: a.name }))
    .sort((a, b) => b.var_95_1d - a.var_95_1d)
    .slice(0, 10)
}

function portfolioValueChartRows(
  valueSeries: PortfolioValueSeriesVM,
  pnlSeries: PortfolioPnlSeriesVM,
): PortfolioValueChartRow[] {
  return valueSeries.dates.map((date, i) => ({
    date,
    cost: valueSeries.costs[i],
    pnl: valueSeries.values[i] - valueSeries.costs[i],
    value: valueSeries.values[i],
    realized: pnlSeries.realized[i] ?? null,
    totalPnl: pnlSeries.total_pnl[i] ?? null,
  }))
}

function portfolioPnlChartRows(pnlSeries: PortfolioPnlSeriesVM): PortfolioPnlChartRow[] {
  return pnlSeries.dates.map((date, i) => ({
    date,
    unrealized: pnlSeries.values[i],
    realized: pnlSeries.realized[i],
    total: pnlSeries.total_pnl[i],
  }))
}

function positionWeightTop10(assets: RawAsset[]): PositionWeightTop10Item[] {
  return [...assets]
    .map((a) => ({
      ticker: a.ticker,
      weight_pct: toFloat(a.weight_pct),
      profit: toFloat(a.profit),
      value: toFloat(a.value),
      name: a.name,
    }))
    .sort((a, b) => b.weight_pct - a.weight_pct)
    .slice(0, 10)
}

export function filterAssetsByTags(rows: RawAsset[], selectedTags: string[]): RawAsset[] {
  if (!selectedTags.length) return rows
  return rows.filter((r) => selectedTags.some((t) => r.tags.includes(t)))
}

export function presentPortfolioSummary(raw: RawPortfolioSummary): PortfolioSummaryVM {
  const { assets, assets_history, portfolio_history, portfolio_current_snapshot, available_tags } = raw
  const valueSeries = portfolioValueSeries(portfolio_history)
  const pnlSeries = portfolioPnlSeries(portfolio_history)
  return {
    kpi: kpi(portfolio_current_snapshot, portfolio_history),
    asset_table: assetTable(assets),
    portfolio_value_series: valueSeries,
    portfolio_pnl_series: pnlSeries,
    portfolio_drawdown: portfolioDrawdown(portfolio_history),
    position_weight_series: positionWeightSeries(assets),
    position_distribution: positionDistribution(assets),
    winners: topWinners(assets),
    losers: topLosers(assets),
    daily_movers: dailyMovers(assets),
    var_by_position: varByPosition(assets),
    portfolio_fx_attribution: portfolioFxAttribution(portfolio_history),
    profitability: profitability(assets),
    portfolio_value_chart_rows: portfolioValueChartRows(valueSeries, pnlSeries),
    portfolio_pnl_chart_rows: portfolioPnlChartRows(pnlSeries),
    position_weight_top10: positionWeightTop10(assets),
    losers_pnl: losersPnl(assets_history),
    available_tags,
  }
}
