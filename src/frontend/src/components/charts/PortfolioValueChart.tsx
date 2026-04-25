import { useTheme } from '@mui/material'
import {
  ComposedChart,
  Area,
  Bar,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
  ReferenceLine,
} from 'recharts'
import { fmtNum } from '../../utils/chartUtils'

interface PortfolioValueChartProps {
  valueSeries?: { dates: string[]; values: number[]; costs: number[] }
  pnlSeries?: { dates: string[]; values: number[]; realized: number[]; total_pnl: number[] }
}

export default function PortfolioValueChart({ valueSeries, pnlSeries }: PortfolioValueChartProps) {
  const theme = useTheme()
  if (!valueSeries?.dates?.length) return null

  const data = valueSeries.dates.map((d, i) => ({
    date: d,
    cost: valueSeries.costs[i],
    pnl: valueSeries.values[i] - valueSeries.costs[i],
    value: valueSeries.values[i],
    realized: pnlSeries?.realized[i] ?? null,
    totalPnl: pnlSeries?.total_pnl[i] ?? null,
  }))

  type DataPoint = typeof data[number]

  function CustomTooltip({ active, payload }: { active?: boolean; payload?: unknown[] }) {
    if (!active || !payload?.length) return null
    const d = (payload as Array<{ payload: DataPoint }>)[0].payload
    const unrealizedPositive = d.pnl >= 0
    const realizedPositive = (d.realized ?? 0) >= 0
    const totalPositive = (d.totalPnl ?? 0) >= 0
    return (
      <div style={{ background: theme.palette.background.paper, border: `1px solid ${theme.palette.divider}`, padding: '6px 10px', fontSize: 11, borderRadius: 4 }}>
        <div style={{ marginBottom: 4, color: theme.palette.text.secondary, fontSize: 10 }}>{d.date}</div>
        <div>Value: {fmtNum(d.value)}</div>
        <div>Cost: {fmtNum(d.cost)}</div>
        <div style={{ color: unrealizedPositive ? theme.palette.success.main : theme.palette.error.main }}>
          Unrealized: {unrealizedPositive ? '+' : ''}{fmtNum(d.pnl)}
        </div>
        {d.realized != null && (
          <div style={{ color: realizedPositive ? theme.palette.success.main : theme.palette.error.main }}>
            Realized: {realizedPositive ? '+' : ''}{fmtNum(d.realized)}
          </div>
        )}
        {d.totalPnl != null && (
          <div style={{ color: totalPositive ? theme.palette.success.main : theme.palette.error.main, fontWeight: 600 }}>
            Total P&amp;L: {totalPositive ? '+' : ''}{fmtNum(d.totalPnl)}
          </div>
        )}
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <ComposedChart data={data} margin={{ top: 4, right: 50, bottom: 0, left: 0 }}>
        <defs>
          <linearGradient id="pnlGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={theme.palette.success.main} stopOpacity={0.4} />
            <stop offset="95%" stopColor={theme.palette.success.main} stopOpacity={0.05} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
        <XAxis dataKey="date" tick={{ fontSize: 10 }} tickLine={false} />
        <YAxis yAxisId="value" tick={{ fontSize: 10 }} tickLine={false} width={60} />
        <YAxis yAxisId="pnl" orientation="right" tick={{ fontSize: 10 }} tickLine={false} width={50} />
        <Tooltip content={<CustomTooltip />} />
        <Legend iconSize={10} wrapperStyle={{ fontSize: 11 }} />
        <ReferenceLine yAxisId="pnl" y={0} stroke={theme.palette.divider} strokeDasharray="3 3" />

        {/* Left axis: cost base (dashed, transparent) + unrealized P&L gap (green fill) */}
        <Area yAxisId="value" type="monotone" dataKey="cost" stackId="val"
          stroke={theme.palette.text.secondary} fill="transparent"
          strokeDasharray="4 2" strokeWidth={1} dot={false} legendType="none" name="Cost Basis" />
        <Area yAxisId="value" type="monotone" dataKey="pnl" stackId="val"
          stroke={theme.palette.primary.main} fill="url(#pnlGrad)"
          strokeWidth={1.5} dot={false} legendType="none" name="Portfolio Value" />

        {/* Right axis: realized P&L bars + total P&L line */}
        {pnlSeries && <>
          <Bar yAxisId="pnl" dataKey="realized" name="Realized P&L"
            fill={theme.palette.secondary.main} opacity={0.7} barSize={3} />
          <Line yAxisId="pnl" type="monotone" dataKey="totalPnl" name="Total P&L"
            stroke={theme.palette.success.main} strokeWidth={1.5} dot={false} />
        </>}
      </ComposedChart>
    </ResponsiveContainer>
  )
}
