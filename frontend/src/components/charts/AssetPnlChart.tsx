import { useTheme } from '@mui/material'
import { ComposedChart, Bar, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine, Legend } from 'recharts'
import { useTooltipStyle } from '../../utils/chartUtils'

interface AssetPnlChartProps {
  series?: {
    dates: string[]
    values: (number | null)[]
    high_30d?: (number | null)[]
    low_30d?: (number | null)[]
  }
}

export default function AssetPnlChart({ series }: AssetPnlChartProps) {
  const theme = useTheme()
  const tooltipStyle = useTooltipStyle()
  if (!series?.dates?.length) return null

  const data = series.dates.map((d, i) => ({
    date: d,
    profit: series.values[i],
    high: series.high_30d?.[i],
    low: series.low_30d?.[i],
  }))

  return (
    <ResponsiveContainer width="100%" height={180}>
      <ComposedChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
        <XAxis dataKey="date" tick={{ fontSize: 10 }} tickLine={false} />
        <YAxis tick={{ fontSize: 10 }} tickLine={false} width={60} />
        <Tooltip contentStyle={tooltipStyle} />
        <Legend iconSize={10} wrapperStyle={{ fontSize: 11 }} />
        <ReferenceLine y={0} stroke={theme.palette.divider} />
        <Bar dataKey="profit" name="P&L" fill={theme.palette.primary.main} opacity={0.7} />
        <Line type="monotone" dataKey="high" name="30d High" stroke={theme.palette.success.main} strokeDasharray="3 2" strokeWidth={1} dot={false} />
        <Line type="monotone" dataKey="low" name="30d Low" stroke={theme.palette.error.main} strokeDasharray="3 2" strokeWidth={1} dot={false} />
      </ComposedChart>
    </ResponsiveContainer>
  )
}
