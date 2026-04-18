import { useTheme } from '@mui/material'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts'
import { useTooltipStyle, fmtNum } from '../../utils/chartUtils'

interface PortfolioValueChartProps {
  series?: { dates: string[]; values: number[]; costs: number[] }
}

export default function PortfolioValueChart({ series }: PortfolioValueChartProps) {
  const theme = useTheme()
  const tooltipStyle = useTooltipStyle()
  if (!series?.dates?.length) return null

  const data = series.dates.map((d, i) => ({
    date: d,
    cost: series.costs[i],
    pnl: series.values[i] - series.costs[i],
    value: series.values[i],
  }))

  function CustomTooltip({ active, payload }: { active?: boolean; payload?: unknown[] }) {
    if (!active || !payload?.length) return null
    const d = (payload as Array<{ payload: typeof data[number] }>)[0].payload
    const isPositive = d.pnl >= 0
    return (
      <div style={{ background: theme.palette.background.paper, border: `1px solid ${theme.palette.divider}`, padding: '6px 10px', fontSize: 11, borderRadius: 4 }}>
        <div style={{ marginBottom: 2, color: theme.palette.text.secondary, fontSize: 10 }}>{d.date}</div>
        <div>Value: {fmtNum(d.value)}</div>
        <div>Cost: {fmtNum(d.cost)}</div>
        <div style={{ color: isPositive ? theme.palette.success.main : theme.palette.error.main }}>
          P&L: {isPositive ? '+' : ''}{fmtNum(d.pnl)}
        </div>
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
        <defs>
          <linearGradient id="pnlGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={theme.palette.success.main} stopOpacity={0.4} />
            <stop offset="95%" stopColor={theme.palette.success.main} stopOpacity={0.05} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
        <XAxis dataKey="date" tick={{ fontSize: 10 }} tickLine={false} />
        <YAxis tick={{ fontSize: 10 }} tickLine={false} width={60} />
        <Tooltip content={<CustomTooltip />} />
        {/* Base: cost line — transparent fill, dashed stroke */}
        <Area
          type="monotone"
          dataKey="cost"
          stackId="pv"
          stroke={theme.palette.text.secondary}
          fill="transparent"
          strokeDasharray="4 2"
          strokeWidth={1}
          dot={false}
          name="Total Cost"
          legendType="none"
        />
        {/* Gap: P&L above cost — green fill highlights the gain */}
        <Area
          type="monotone"
          dataKey="pnl"
          stackId="pv"
          stroke={theme.palette.primary.main}
          fill="url(#pnlGrad)"
          strokeWidth={1.5}
          dot={false}
          name="Portfolio Value"
          legendType="none"
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
