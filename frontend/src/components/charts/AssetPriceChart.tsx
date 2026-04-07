import { useTheme } from '@mui/material'
import { ComposedChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts'
import { useTooltipStyle } from '../../utils/chartUtils'

interface AssetPriceChartProps {
  series?: {
    dates: string[]
    values: (number | null)[]
    value_ma_30d?: (number | null)[]
    value_ma_50d?: (number | null)[]
  }
}

export default function AssetPriceChart({ series }: AssetPriceChartProps) {
  const theme = useTheme()
  const tooltipStyle = useTooltipStyle()
  if (!series?.dates?.length) return null

  const data = series.dates.map((d, i) => ({
    date: d,
    price: series.values[i],
    ma30: series.value_ma_30d?.[i],
    ma50: series.value_ma_50d?.[i],
  }))

  return (
    <ResponsiveContainer width="100%" height={200}>
      <ComposedChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
        <XAxis dataKey="date" tick={{ fontSize: 10 }} tickLine={false} />
        <YAxis tick={{ fontSize: 10 }} tickLine={false} width={60} />
        <Tooltip contentStyle={tooltipStyle} />
        <Legend iconSize={10} wrapperStyle={{ fontSize: 11 }} />
        <Line type="monotone" dataKey="price" name="Price" stroke={theme.palette.primary.main} strokeWidth={1.5} dot={false} />
        <Line type="monotone" dataKey="ma30" name="MA 30d" stroke={theme.palette.warning.main} strokeWidth={1} strokeDasharray="4 2" dot={false} />
        <Line type="monotone" dataKey="ma50" name="MA 50d" stroke={theme.palette.secondary.main} strokeWidth={1} strokeDasharray="4 2" dot={false} />
      </ComposedChart>
    </ResponsiveContainer>
  )
}
