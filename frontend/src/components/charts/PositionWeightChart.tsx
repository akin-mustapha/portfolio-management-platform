import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import { useTheme } from '@mui/material'
import { useTooltipStyle } from '../../utils/chartUtils'

interface PositionWeightChartProps {
  distribution?: Array<{ ticker: string; weight_pct: number; profit: number; value: number }>
}

// Reordered so high-contrast colors are never adjacent in the ring
const PALETTE = [
  '#0d6efd', // blue
  '#e83e8c', // pink
  '#fd7e14', // orange
  '#6f42c1', // purple
  '#ffc107', // yellow
  '#17a2b8', // cyan
  '#ff6b6b', // coral
  '#dc3545', // red
  '#20c997', // teal
  '#28a745', // green
  '#6c757d', // gray
]

export default function PositionWeightChart({ distribution }: PositionWeightChartProps) {
  const theme = useTheme()
  const tooltipStyle = useTooltipStyle()
  if (!distribution?.length) return null

  const sorted = [...distribution].sort((a, b) => b.weight_pct - a.weight_pct).slice(0, 10)

  const textSecondary = theme.palette.text.secondary
  const textPrimary = theme.palette.text.primary

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, width: '100%', height: 300, padding: '10px' }}>
      {/* Donut */}
      <div style={{ flex: '0 0 55%', height: '100%' }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={sorted}
              dataKey="weight_pct"
              nameKey="ticker"
              cx="50%"
              cy="50%"
              outerRadius={120}
              innerRadius={62}
              paddingAngle={2}
            >
              {sorted.map((_, i) => (
                <Cell key={i} fill={PALETTE[i % PALETTE.length]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={tooltipStyle}
              formatter={(v: unknown) => [`${Number(v).toFixed(2)}%`, 'Weight']}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Ranked legend */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 7, overflowY: 'auto', maxHeight: 300 }}>
        {sorted.map((item, i) => (
          <div
            key={item.ticker}
            style={{ display: 'flex', alignItems: 'center', gap: 8 }}
          >
            {/* Rank */}
            <span style={{ fontSize: 10, color: textSecondary, width: 14, textAlign: 'right', flexShrink: 0 }}>
              {i + 1}
            </span>
            {/* Color dot */}
            <span style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              backgroundColor: PALETTE[i % PALETTE.length],
              flexShrink: 0,
            }} />
            {/* Ticker */}
            <span style={{ fontSize: 11, color: textPrimary, width: 52, fontWeight: 500 }}>
              {item.ticker}
            </span>
            {/* Weight */}
            <span style={{ fontSize: 11, color: textSecondary, flexShrink: 0 }}>
              {item.weight_pct.toFixed(1)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
