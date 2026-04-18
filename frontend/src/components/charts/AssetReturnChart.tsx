import { useTheme } from '@mui/material'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from 'recharts'
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
      <AreaChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
        <defs>
          <linearGradient id="returnGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={theme.palette.primary.main} stopOpacity={0.3} />
            <stop offset="95%" stopColor={theme.palette.primary.main} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
        <XAxis dataKey="date" tick={{ fontSize: 10 }} tickLine={false} />
        <YAxis tick={{ fontSize: 10 }} tickLine={false} width={50} unit="%" />
        <Tooltip
          contentStyle={tooltipStyle}
          formatter={(v: unknown) => [`${Number(v).toFixed(2)}%`, 'Cumulative Return']}
        />
        <ReferenceLine y={0} stroke={theme.palette.divider} />
        <Area
          type="monotone"
          dataKey="return"
          stroke={theme.palette.primary.main}
          fill="url(#returnGrad)"
          strokeWidth={1.5}
          dot={false}
          baseValue={0}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
