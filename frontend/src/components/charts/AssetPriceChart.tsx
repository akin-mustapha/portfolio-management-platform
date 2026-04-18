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
  if (!series?.dates?.length) return null

  const data = series.dates.map((d, i) => ({
    date: d,
    price: series.values[i],
    ma30: series.price_ma_20d?.[i],
    ma50: series.price_ma_50d?.[i],
  }))

  return (
    <ResponsiveContainer width="100%" height={200}>
      <ComposedChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
        <defs>
          <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={theme.palette.primary.main} stopOpacity={0.2} />
            <stop offset="95%" stopColor={theme.palette.primary.main} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
        <XAxis dataKey="date" tick={{ fontSize: 10 }} tickLine={false} />
        <YAxis tick={{ fontSize: 10 }} tickLine={false} width={60} />
        <Tooltip contentStyle={tooltipStyle} />
        <Legend iconSize={10} wrapperStyle={{ fontSize: 11 }} />
        <Area type="monotone" dataKey="price" name="Price" stroke={theme.palette.primary.main} fill="url(#priceGrad)" strokeWidth={1.5} dot={false} />
        <Line type="monotone" dataKey="ma30" name="MA 20d" stroke={theme.palette.warning.main} strokeWidth={1} strokeDasharray="4 2" dot={false} />
        <Line type="monotone" dataKey="ma50" name="MA 50d" stroke={theme.palette.secondary.main} strokeWidth={1} strokeDasharray="4 2" dot={false} />
      </ComposedChart>
    </ResponsiveContainer>
  )
}
