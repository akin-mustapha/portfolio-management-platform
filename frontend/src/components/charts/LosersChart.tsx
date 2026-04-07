import { useTheme } from '@mui/material'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { useTooltipStyle, fmtNum } from '../../utils/chartUtils'

interface LosersChartProps {
  losers?: Array<{ ticker: string; profit: number; label: string }>
}

export default function LosersChart({ losers }: LosersChartProps) {
  const theme = useTheme()
  const tooltipStyle = useTooltipStyle()
  if (!losers?.length) return null

  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={losers} layout="vertical" margin={{ top: 4, right: 16, bottom: 0, left: 60 }}>
        <XAxis type="number" tick={{ fontSize: 10 }} tickLine={false} />
        <YAxis type="category" dataKey="label" tick={{ fontSize: 10 }} width={60} />
        <Tooltip
          contentStyle={tooltipStyle}
          formatter={(v: unknown) => [fmtNum(v), 'P&L']}
        />
        <Bar dataKey="profit" radius={[0, 3, 3, 0]}>
          {losers.map((_, i) => (
            <Cell key={i} fill={theme.palette.error.main} opacity={1 - i * 0.06} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
