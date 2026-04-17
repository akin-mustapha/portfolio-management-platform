import { Grid } from '@mui/material'
import KpiCard from '../atoms/KpiCard'

interface KpiRowProps {
  kpi?: Record<string, unknown>
  loading?: boolean
}

export default function KpiRow({ kpi, loading = false }: KpiRowProps) {
  const symbol = (kpi?.currency_symbol as string) ?? ''
  const unrealizedPnl = kpi?.unrealized_pnl as number | undefined
  const realizedPnl = kpi?.realized_pnl as number | undefined

  const cards = [
    {
      label: 'Portfolio Value',
      value: kpi?.value as number | undefined,
      prefix: symbol,
      colorCode: 'neutral' as const,
    },
    {
      label: 'Unrealized P&L',
      value: unrealizedPnl,
      prefix: symbol,
      colorCode: unrealizedPnl != null ? (unrealizedPnl >= 0 ? 'positive' : 'negative') : 'neutral',
    } as const,
    {
      label: 'Realized P&L',
      value: realizedPnl,
      prefix: symbol,
      colorCode: realizedPnl != null ? (realizedPnl >= 0 ? 'positive' : 'negative') : 'neutral',
    } as const,
    {
      label: 'Total Cost',
      value: kpi?.total_cost as number | undefined,
      prefix: symbol,
      colorCode: 'neutral' as const,
    },
    {
      label: 'Cash',
      value: kpi?.cash as number | undefined,
      prefix: symbol,
      colorCode: 'neutral' as const,
    },
    {
      label: 'Daily Change',
      value: kpi?.daily_value_change_pct as number | undefined,
      suffix: '%',
      colorCode: ((kpi?.daily_value_change_pct as number) ?? 0) >= 0 ? 'positive' : 'negative',
      metricKey: 'daily_change_pct',
    } as const,
    {
      label: 'Vol (weighted)',
      value: kpi?.portfolio_vol as number | undefined,
      suffix: '%',
      colorCode: 'neutral' as const,
      metricKey: 'portfolio_volatility_30d',
    } as const,
  ]

  return (
    <Grid container spacing={1} sx={{ mb: 1 }}>
      {cards.map((card) => (
        <Grid key={card.label} size={{ xs: 6, sm: 4, md: 3, lg: 'auto' }} sx={{ flexGrow: 1 }}>
          <KpiCard {...card} loading={loading} compact />
        </Grid>
      ))}
    </Grid>
  )
}
