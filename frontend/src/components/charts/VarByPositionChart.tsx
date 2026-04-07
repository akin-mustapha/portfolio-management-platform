import { useTheme } from '@mui/material'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts'
import { useTooltipStyle } from '../../utils/chartUtils'

interface VarByPositionChartProps {
  varData?: Array<{ ticker: string; var_95_1d: number }>
}

export default function VarByPositionChart({ varData }: VarByPositionChartProps) {
  const theme = useTheme()
  const tooltipStyle = useTooltipStyle()
  if (!varData?.length) return null

  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={varData} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
        <XAxis dataKey="ticker" tick={{ fontSize: 10 }} tickLine={false} />
        <YAxis tick={{ fontSize: 10 }} tickLine={false} width={55} />
        <Tooltip
          contentStyle={tooltipStyle}
          formatter={(v: unknown) => [Number(v).toFixed(4), 'VaR 95% 1d']}
        />
        <Bar dataKey="var_95_1d" radius={[3, 3, 0, 0]}>
          {varData.map((_, i) => (
            <Cell key={i} fill={theme.palette.error.main} opacity={0.9 - i * 0.06} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
