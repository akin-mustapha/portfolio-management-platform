import { useTheme } from '@mui/material'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from 'recharts'
import { useTooltipStyle } from '../../utils/chartUtils'

interface AssetReturnChartProps {
  cumulativeSeries?: { dates: string[]; values: (number | null)[] }
}

export default function AssetReturnChart({ cumulativeSeries }: AssetReturnChartProps) {
  const theme = useTheme()
  const tooltipStyle = useTooltipStyle()
  if (!cumulativeSeries?.dates?.length) return null

  const data = cumulativeSeries.dates.map((d, i) => ({
    date: d,
    return: cumulativeSeries.values[i] != null ? Number(cumulativeSeries.values[i]) * 100 : null,
  }))

  return (
    <ResponsiveContainer width="100%" height={180}>
      <LineChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
        <XAxis dataKey="date" tick={{ fontSize: 10 }} tickLine={false} />
        <YAxis tick={{ fontSize: 10 }} tickLine={false} width={50} unit="%" />
        <Tooltip
          contentStyle={tooltipStyle}
          formatter={(v: unknown) => [`${Number(v).toFixed(2)}%`, 'Cumulative Return']}
        />
        <ReferenceLine y={0} stroke={theme.palette.divider} />
        <Line type="monotone" dataKey="return" stroke={theme.palette.primary.main} strokeWidth={1.5} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  )
}
