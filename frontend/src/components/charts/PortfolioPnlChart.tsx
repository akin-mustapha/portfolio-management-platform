import { useTheme } from '@mui/material'
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
  ReferenceLine,
} from 'recharts'
import { useTooltipStyle, fmtNum } from '../../utils/chartUtils'

interface PortfolioPnlChartProps {
  series?: { dates: string[]; values: number[]; realized: number[]; total_pnl: number[] }
}

export default function PortfolioPnlChart({ series }: PortfolioPnlChartProps) {
  const theme = useTheme()
  const tooltipStyle = useTooltipStyle()
  if (!series?.dates?.length) return null

  const data = series.dates.map((d, i) => ({
    date: d,
    unrealized: series.values[i],
    realized: series.realized[i],
    total: series.total_pnl[i],
  }))

  return (
    <ResponsiveContainer width="100%" height={220}>
      <ComposedChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
        <XAxis dataKey="date" tick={{ fontSize: 10 }} tickLine={false} />
        <YAxis tick={{ fontSize: 10 }} tickLine={false} width={60} />
        <Tooltip
          contentStyle={tooltipStyle}
          formatter={(v: unknown) => [fmtNum(v), '']}
        />
        <Legend iconSize={10} wrapperStyle={{ fontSize: 11 }} />
        <ReferenceLine y={0} stroke={theme.palette.divider} />
        <Bar dataKey="unrealized" name="Unrealized P&L" fill={theme.palette.primary.main} opacity={0.6} />
        <Line type="monotone" dataKey="total" name="Total P&L" stroke={theme.palette.success.main} strokeWidth={1.5} dot={false} />
      </ComposedChart>
    </ResponsiveContainer>
  )
}
