import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { useTooltipStyle } from '../../utils/chartUtils'

interface PositionWeightChartProps {
  distribution?: Array<{ ticker: string; weight_pct: number; profit: number; value: number }>
}

const PALETTE = ['#0d6efd','#fd7e14','#6f42c1','#20c997','#e83e8c','#ffc107','#17a2b8','#dc3545','#28a745','#6c757d']

export default function PositionWeightChart({ distribution }: PositionWeightChartProps) {
  const tooltipStyle = useTooltipStyle()
  if (!distribution?.length) return null

  const data = distribution.slice(0, 10)

  return (
    <ResponsiveContainer width="100%" height={240}>
      <PieChart>
        <Pie
          data={data}
          dataKey="weight_pct"
          nameKey="ticker"
          cx="50%"
          cy="50%"
          outerRadius={90}
          innerRadius={40}
          paddingAngle={2}
        >
          {data.map((_, i) => (
            <Cell key={i} fill={PALETTE[i % PALETTE.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={tooltipStyle}
          formatter={(v: unknown) => [`${Number(v).toFixed(2)}%`, 'Weight']}
        />
        <Legend iconSize={10} wrapperStyle={{ fontSize: 11 }} />
      </PieChart>
    </ResponsiveContainer>
  )
}
