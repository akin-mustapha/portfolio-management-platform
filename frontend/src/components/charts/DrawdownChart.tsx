import { useTheme } from '@mui/material'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from 'recharts'
import { useTooltipStyle } from '../../utils/chartUtils'

interface DrawdownChartProps {
  drawdown?: { dates: string[]; drawdown_pct: number[] }
}

export default function DrawdownChart({ drawdown }: DrawdownChartProps) {
  const theme = useTheme()
  const tooltipStyle = useTooltipStyle()
  if (!drawdown?.dates?.length) return null

  const data = drawdown.dates.map((d, i) => ({ date: d, drawdown: drawdown.drawdown_pct[i] }))

  return (
    <ResponsiveContainer width="100%" height={180}>
      <AreaChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
        <defs>
          <linearGradient id="ddGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={theme.palette.error.main} stopOpacity={0.4} />
            <stop offset="95%" stopColor={theme.palette.error.main} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
        <XAxis dataKey="date" tick={{ fontSize: 10 }} tickLine={false} />
        <YAxis tick={{ fontSize: 10 }} tickLine={false} width={50} />
        <Tooltip
          contentStyle={tooltipStyle}
          formatter={(v: unknown) => [`${Number(v).toFixed(2)}%`, 'Drawdown']}
        />
        <ReferenceLine y={0} stroke={theme.palette.divider} />
        <Area type="monotone" dataKey="drawdown" stroke={theme.palette.error.main} fill="url(#ddGrad)" strokeWidth={1.5} dot={false} />
      </AreaChart>
    </ResponsiveContainer>
  )
}
