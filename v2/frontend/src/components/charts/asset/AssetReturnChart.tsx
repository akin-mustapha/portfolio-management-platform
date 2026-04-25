import { useMemo } from 'react'
import { useTheme } from '@mui/material'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from 'recharts'
import { useTooltipStyle } from '../../utils/chartUtils'
import type { AssetReturnSeriesVM } from '../../presenters/assetPresenter'

interface AssetReturnChartProps {
  /** Values are already in % (multiplied by 100 in the presenter) */
  cumulativeSeries?: AssetReturnSeriesVM
}

export default function AssetReturnChart({ cumulativeSeries }: AssetReturnChartProps) {
  const theme = useTheme()
  const tooltipStyle = useTooltipStyle()
  const data = useMemo(
    () =>
      (cumulativeSeries?.dates ?? []).map((d, i) => ({
        date: d,
        return: cumulativeSeries?.values[i],
      })),
    [cumulativeSeries?.dates, cumulativeSeries?.values],
  )
  if (!cumulativeSeries?.dates?.length) return null
  const color = theme.palette.primary.main

  return (
    <ResponsiveContainer width="100%" height={180}>
      <AreaChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
        <defs>
          <linearGradient id="retGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.28} />
            <stop offset="100%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} strokeOpacity={0.5} vertical={false} />
        <XAxis dataKey="date" tick={{ fontSize: 10 }} tickLine={false} axisLine={{ stroke: theme.palette.divider }} />
        <YAxis tick={{ fontSize: 10 }} tickLine={false} axisLine={false} width={50} unit="%" />
        <Tooltip
          contentStyle={tooltipStyle}
          formatter={(v: unknown) => [`${Number(v).toFixed(2)}%`, 'Cumulative Return']}
        />
        <ReferenceLine y={0} stroke={theme.palette.divider} />
        <Area type="monotone" dataKey="return" stroke={color} fill="url(#retGrad)" strokeWidth={2.25} dot={false} />
      </AreaChart>
    </ResponsiveContainer>
  )
}
