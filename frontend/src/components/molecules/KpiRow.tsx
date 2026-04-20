<<<<<<< HEAD
import { Box, Divider, Typography, Grid } from '@mui/material'
import KpiCard from '../atoms/KpiCard'
import type { MetricKey } from '../../constants/metricDefinitions'
=======
import { Box } from '@mui/material'
import KpiCard from '../atoms/KpiCard'
import KpiGroup, { type KpiGroupItem } from './KpiGroup'
>>>>>>> 74aff6ca946f0bd151cffbd68dda9e801cfa3223

interface KpiRowProps {
  kpi?: Record<string, unknown>
  valueSeries?: { values?: number[]; costs?: number[] }
  pnlSeries?: { values?: number[] }
  loading?: boolean
}

<<<<<<< HEAD
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
=======
type CardDef = KpiGroupItem & { colorCode: 'positive' | 'negative' | 'neutral' }

export default function KpiRow({ kpi, valueSeries, pnlSeries, loading = false }: KpiRowProps) {
>>>>>>> 74aff6ca946f0bd151cffbd68dda9e801cfa3223
  const symbol = (kpi?.currency_symbol as string) ?? ''
  const unrealizedPnl = kpi?.unrealized_pnl as number | undefined
  const realizedPnl = kpi?.realized_pnl as number | undefined
  const dailyChange = kpi?.daily_value_change_pct as number | undefined

  const vsBenchmark = kpi?.portfolio_vs_benchmark_30d as number | undefined

<<<<<<< HEAD
  const performanceCards: CardDef[] = [
    { label: 'Portfolio Value', value: kpi?.value as number | undefined, prefix: symbol, colorCode: 'neutral' },
    { label: 'Total Invested', value: kpi?.total_cost as number | undefined, prefix: symbol, colorCode: 'neutral' },
    {
      label: 'Unrealized P&L', value: unrealizedPnl, prefix: symbol,
      colorCode: unrealizedPnl != null ? (unrealizedPnl >= 0 ? 'positive' : 'negative') : 'neutral',
=======
  const portfolioValue = kpi?.value as number | undefined
  const heroSub =
    dailyChange != null
      ? `${dailyChange >= 0 ? '+' : ''}${dailyChange.toFixed(2)}% today`
      : undefined

  const supportingCards: CardDef[] = [
    {
      label: 'Total Invested',
      value: kpi?.total_cost as number | undefined,
      prefix: symbol,
      colorCode: 'neutral',
      sparkline: valueSeries?.costs,
    },
    {
      label: 'Unrealized P&L',
      value: unrealizedPnl,
      prefix: symbol,
      colorCode: unrealizedPnl != null ? (unrealizedPnl >= 0 ? 'positive' : 'negative') : 'neutral',
      sparkline: pnlSeries?.values,
>>>>>>> 74aff6ca946f0bd151cffbd68dda9e801cfa3223
    },
    {
      label: 'Realized P&L', value: realizedPnl, prefix: symbol,
      colorCode: realizedPnl != null ? (realizedPnl >= 0 ? 'positive' : 'negative') : 'neutral',
    },
    {
<<<<<<< HEAD
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
=======
      label: 'Vol (weighted)',
      value: kpi?.portfolio_vol as number | undefined,
      suffix: '%',
      colorCode: 'neutral',
      metricKey: 'portfolio_volatility_30d',
    },
    {
      label: 'Beta',
      value: kpi?.portfolio_beta as number | undefined,
      colorCode: 'neutral',
      metricKey: 'portfolio_beta',
    },
    {
      label: 'Sharpe 30D',
      value: kpi?.sharpe_ratio_30d as number | undefined,
>>>>>>> 74aff6ca946f0bd151cffbd68dda9e801cfa3223
      colorCode: ((kpi?.sharpe_ratio_30d as number) ?? 0) >= 1 ? 'positive' : 'neutral',
      metricKey: 'portfolio_sharpe_30d',
    },
    {
<<<<<<< HEAD
      label: 'vs SP500 30D', value: vsBenchmark, suffix: '%',
=======
      label: 'vs SP500 30D',
      value: vsBenchmark,
      suffix: '%',
>>>>>>> 74aff6ca946f0bd151cffbd68dda9e801cfa3223
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
<<<<<<< HEAD
    <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-end', mb: 1, flexWrap: 'wrap' }}>
      <KpiGroup label="Performance" cards={performanceCards} loading={loading} />
      <Divider orientation="vertical" flexItem sx={{ alignSelf: 'stretch', mx: 0.5 }} />
      <KpiGroup label="Cash" cards={cashCards} loading={loading} />
=======
    <Box sx={{ display: 'flex', gap: 1, alignItems: 'stretch', mb: 1, flexWrap: 'wrap' }}>
      <Box
        sx={(theme) => ({
          flex: '1.4 1 340px',
          minWidth: 0,
          display: 'flex',
          position: 'relative',
          borderRadius: 3,
          border: '1px solid',
          borderColor: theme.palette.mode === 'dark' ? 'rgba(107,140,255,0.32)' : 'rgba(59,91,255,0.26)',
          bgcolor: 'background.paper',
          boxShadow: theme.palette.mode === 'dark'
            ? '0 1px 2px rgba(0,0,0,0.24), 0 12px 36px -12px rgba(107,140,255,0.32)'
            : '0 1px 2px rgba(15,23,42,0.04), 0 12px 36px -14px rgba(59,91,255,0.28)',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            inset: 0,
            background: theme.palette.mode === 'dark'
              ? 'radial-gradient(130% 90% at 0% 0%, rgba(107,140,255,0.18) 0%, rgba(107,140,255,0) 60%)'
              : 'radial-gradient(130% 90% at 0% 0%, rgba(59,91,255,0.14) 0%, rgba(59,91,255,0) 60%)',
            pointerEvents: 'none',
          },
          transition: 'box-shadow 180ms ease, border-color 180ms ease',
        })}
      >
        <Box sx={{ flex: 1 }}>
          <KpiCard
            variant="hero"
            label="Portfolio Value"
            value={portfolioValue}
            prefix={symbol}
            subValue={heroSub}
            colorCode={dailyChange != null ? (dailyChange >= 0 ? 'positive' : 'negative') : 'neutral'}
            sparkline={valueSeries?.values}
            loading={loading}
          />
        </Box>
      </Box>

      <Box sx={{ flex: '3 1 560px', minWidth: 0, display: 'flex' }}>
        <KpiGroup label="Performance" cards={supportingCards} loading={loading} />
      </Box>
      <Box sx={{ flex: '1 1 240px', minWidth: 0, display: 'flex' }}>
        <KpiGroup label="Cash" cards={cashCards} loading={loading} />
      </Box>
>>>>>>> 74aff6ca946f0bd151cffbd68dda9e801cfa3223
    </Box>
  )
}
