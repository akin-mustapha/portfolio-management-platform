import { Box, Divider, Typography, Grid } from '@mui/material'
import KpiCard from '../atoms/KpiCard'
import type { MetricKey } from '../../constants/metricDefinitions'

interface KpiRowProps {
  kpi?: Record<string, unknown>
  loading?: boolean
}

interface CardDef {
  label: string
  value?: number | string | null
  prefix?: string
  suffix?: string
  colorCode: 'positive' | 'negative' | 'neutral'
  metricKey?: MetricKey
}

function KpiGroup({ label, cards, loading }: { label: string; cards: CardDef[]; loading: boolean }) {
  return (
    <Box>
      <Typography variant="caption" color="text.disabled" fontWeight={600} letterSpacing={1} sx={{ textTransform: 'uppercase', display: 'block', mb: 0.5, fontSize: 10 }}>
        {label}
      </Typography>
      <Grid container spacing={0.75}>
        {cards.map((card) => (
          <Grid key={card.label} size={{ xs: 6, sm: 'auto' }} sx={{ flexGrow: 1 }}>
            <KpiCard {...card} loading={loading} compact />
          </Grid>
        ))}
      </Grid>
    </Box>
  )
}

export default function KpiRow({ kpi, loading = false }: KpiRowProps) {
  const symbol = (kpi?.currency_symbol as string) ?? ''
  const unrealizedPnl = kpi?.unrealized_pnl as number | undefined
  const realizedPnl = kpi?.realized_pnl as number | undefined

  const vsBenchmark = kpi?.portfolio_vs_benchmark_30d as number | undefined

  const performanceCards: CardDef[] = [
    { label: 'Portfolio Value', value: kpi?.value as number | undefined, prefix: symbol, colorCode: 'neutral' },
    { label: 'Total Invested', value: kpi?.total_cost as number | undefined, prefix: symbol, colorCode: 'neutral' },
    {
      label: 'Unrealized P&L', value: unrealizedPnl, prefix: symbol,
      colorCode: unrealizedPnl != null ? (unrealizedPnl >= 0 ? 'positive' : 'negative') : 'neutral',
    },
    {
      label: 'Realized P&L', value: realizedPnl, prefix: symbol,
      colorCode: realizedPnl != null ? (realizedPnl >= 0 ? 'positive' : 'negative') : 'neutral',
    },
    {
      label: 'Daily Change', value: kpi?.daily_value_change_pct as number | undefined, suffix: '%',
      colorCode: ((kpi?.daily_value_change_pct as number) ?? 0) >= 0 ? 'positive' : 'negative',
      metricKey: 'daily_change_pct',
    },
    { label: 'Vol (weighted)', value: kpi?.portfolio_vol as number | undefined, suffix: '%', colorCode: 'neutral', metricKey: 'portfolio_volatility_30d' },
    {
      label: 'Beta', value: kpi?.portfolio_beta as number | undefined,
      colorCode: 'neutral', metricKey: 'portfolio_beta',
    },
    {
      label: 'Sharpe 30D', value: kpi?.sharpe_ratio_30d as number | undefined,
      colorCode: ((kpi?.sharpe_ratio_30d as number) ?? 0) >= 1 ? 'positive' : 'neutral',
      metricKey: 'portfolio_sharpe_30d',
    },
    {
      label: 'vs SP500 30D', value: vsBenchmark, suffix: '%',
      colorCode: vsBenchmark != null ? (vsBenchmark >= 0 ? 'positive' : 'negative') : 'neutral',
      metricKey: 'portfolio_vs_sp500_30d',
    },
  ]

  const cashCards: CardDef[] = [
    { label: 'Cash Available', value: kpi?.cash as number | undefined, prefix: symbol, colorCode: 'neutral' },
    { label: 'Cash Reserved', value: kpi?.cash_reserved as number | undefined, prefix: symbol, colorCode: 'neutral' },
    { label: 'Cash in Pies', value: kpi?.cash_in_pies as number | undefined, prefix: symbol, colorCode: 'neutral' },
  ]

  return (
    <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-end', mb: 1, flexWrap: 'wrap' }}>
      <KpiGroup label="Performance" cards={performanceCards} loading={loading} />
      <Divider orientation="vertical" flexItem sx={{ alignSelf: 'stretch', mx: 0.5 }} />
      <KpiGroup label="Cash" cards={cashCards} loading={loading} />
    </Box>
  )
}
