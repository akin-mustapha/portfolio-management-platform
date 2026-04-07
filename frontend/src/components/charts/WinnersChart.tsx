import { useTheme } from '@mui/material'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { useTooltipStyle, fmtNum } from '../../utils/chartUtils'

interface WinnersChartProps {
  winners?: Array<{ ticker: string; profit: number; label: string }>
}

export default function WinnersChart({ winners }: WinnersChartProps) {
  const theme = useTheme()
  const tooltipStyle = useTooltipStyle()
  if (!winners?.length) return null

  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={winners} layout="vertical" margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
        <XAxis type="number" tick={{ fontSize: 10 }} tickLine={false} />
        <YAxis type="category" dataKey="label" tick={{ fontSize: 10 }} width={60} />
        <Tooltip
          contentStyle={tooltipStyle}
          formatter={(v: unknown) => [fmtNum(v), 'Profit']}
        />
        <Bar dataKey="profit" radius={[0, 3, 3, 0]}>
          {winners.map((_, i) => (
            <Cell key={i} fill={theme.palette.success.main} opacity={1 - i * 0.06} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
