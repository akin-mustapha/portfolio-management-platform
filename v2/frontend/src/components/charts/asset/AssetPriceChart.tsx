import { useMemo } from 'react'
import { useTheme } from '@mui/material'
import { ComposedChart, Area, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts'
import { useTooltipStyle } from '../../utils/chartUtils'

interface AssetPriceChartProps {
  series?: {
    dates: string[]
    values: (number | null)[]
    price_ma_20d?: (number | null)[]
    price_ma_50d?: (number | null)[]
  }
}

export default function AssetPriceChart({ series }: AssetPriceChartProps) {
  const theme = useTheme()
  const tooltipStyle = useTooltipStyle()
  const data = useMemo(
    () =>
      (series?.dates ?? []).map((d, i) => ({
        date: d,
        price: series?.values[i],
        ma30: series?.price_ma_20d?.[i],
        ma50: series?.price_ma_50d?.[i],
      })),
    [series?.dates, series?.values, series?.price_ma_20d, series?.price_ma_50d],
  )
  if (!series?.dates?.length) return null

  return (
    <ResponsiveContainer width="100%" height={200}>
      <ComposedChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} strokeOpacity={0.5} vertical={false} />
        <XAxis dataKey="date" tick={{ fontSize: 10 }} tickLine={false} axisLine={{ stroke: theme.palette.divider }} />
        <YAxis tick={{ fontSize: 10 }} tickLine={false} axisLine={false} width={60} />
        <Tooltip contentStyle={tooltipStyle} />
        <Legend iconSize={10} wrapperStyle={{ fontSize: 11 }} />
        <Line type="monotone" dataKey="price" name="Price" stroke={theme.palette.primary.main} strokeWidth={2.25} dot={false} />
        <Line type="monotone" dataKey="ma30" name="MA 20d" stroke={theme.palette.warning.main} strokeWidth={1.25} strokeDasharray="4 2" dot={false} />
        <Line type="monotone" dataKey="ma50" name="MA 50d" stroke={theme.palette.secondary.main} strokeWidth={1.25} strokeDasharray="4 2" dot={false} />
      </ComposedChart>
    </ResponsiveContainer>
  )
}
