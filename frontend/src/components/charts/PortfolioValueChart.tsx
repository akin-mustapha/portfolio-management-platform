import { useTheme } from '@mui/material'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
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
    value: series.values[i],
    cost: series.costs[i],
  }))

  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
        <defs>
          <linearGradient id="valueGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={theme.palette.primary.main} stopOpacity={0.3} />
            <stop offset="95%" stopColor={theme.palette.primary.main} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
        <XAxis dataKey="date" tick={{ fontSize: 10 }} tickLine={false} />
        <YAxis tick={{ fontSize: 10 }} tickLine={false} width={60} />
        <Tooltip
          contentStyle={tooltipStyle}
          formatter={(v: unknown) => [fmtNum(v), '']}
        />
        <Legend iconSize={10} wrapperStyle={{ fontSize: 11 }} />
        <Area type="monotone" dataKey="value" name="Portfolio Value" stroke={theme.palette.primary.main} fill="url(#valueGrad)" strokeWidth={1.5} dot={false} />
        <Area type="monotone" dataKey="cost" name="Total Cost" stroke={theme.palette.text.secondary} fill="none" strokeDasharray="4 2" strokeWidth={1} dot={false} />
      </AreaChart>
    </ResponsiveContainer>
  )
}
