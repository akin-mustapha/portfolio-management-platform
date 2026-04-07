import { useTheme } from '@mui/material'
import { LineChart, Line, ResponsiveContainer, ReferenceLine } from 'recharts'

interface SparklineChartProps {
  values?: (number | null)[]
  /** 'positive' | 'negative' | 'neutral' drives line color; defaults to neutral */
  sentiment?: 'positive' | 'negative' | 'neutral'
  height?: number
}

export default function SparklineChart({ values, sentiment = 'neutral', height = 36 }: SparklineChartProps) {
  const theme = useTheme()

  if (!values?.length) return null

  const data = values.map((v, i) => ({ i, v }))

  const color =
    sentiment === 'positive'
      ? theme.palette.success.main
      : sentiment === 'negative'
        ? theme.palette.error.main
        : theme.palette.text.secondary

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 2, right: 2, bottom: 2, left: 2 }}>
        <ReferenceLine y={0} stroke={theme.palette.divider} strokeDasharray="2 2" />
        <Line
          type="monotone"
          dataKey="v"
          stroke={color}
          strokeWidth={1.5}
          dot={false}
          isAnimationActive={false}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
