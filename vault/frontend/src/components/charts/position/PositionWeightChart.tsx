import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import { useTheme } from '@mui/material'
import type { PositionWeightTop10Item } from '../../../presenters/portfolioPresenter'

interface PositionWeightChartProps {
  /** Pre-sorted top-10 by weight — from portfolioPresenter.position_weight_top10 */
  top10?: PositionWeightTop10Item[]
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

export default function PositionWeightChart({ top10 }: PositionWeightChartProps) {
  const theme = useTheme()
  if (!top10?.length) return null

  const textSecondary = theme.palette.text.secondary
  const textPrimary = theme.palette.text.primary

  function CustomTooltip({ active, payload }: { active?: boolean; payload?: unknown[] }) {
    if (!active || !payload?.length) return null
    const d = (payload as Array<{ payload: PositionWeightTop10Item }>)[0].payload
    return (
      <div style={{ background: theme.palette.background.paper, border: `1px solid ${theme.palette.divider}`, padding: '6px 10px', fontSize: 11, borderRadius: 4 }}>
        <div style={{ fontWeight: 600 }}>{d.ticker}</div>
        <div style={{ color: textSecondary, fontSize: 10, marginBottom: 2 }}>{d.name}</div>
        <div>Weight: {d.weight_pct.toFixed(2)}%</div>
      </div>
    )
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, width: '100%', height: 300, padding: '10px' }}>
      <div style={{ flex: '0 0 55%', minWidth: 0, height: '100%' }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={top10}
              dataKey="weight_pct"
              nameKey="ticker"
              cx="50%"
              cy="50%"
              outerRadius={120}
              innerRadius={62}
              paddingAngle={2}
            >
              {top10.map((_, i) => (
                <Cell key={i} fill={PALETTE[i % PALETTE.length]} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 7, overflowY: 'auto', maxHeight: 300 }}>
        {top10.map((item, i) => (
          <div key={item.ticker} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 10, color: textSecondary, width: 14, textAlign: 'right', flexShrink: 0 }}>
              {i + 1}
            </span>
            <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: PALETTE[i % PALETTE.length], flexShrink: 0 }} />
            <span style={{ fontSize: 11, color: textPrimary, width: 52, fontWeight: 500 }}>{item.ticker}</span>
            <span style={{ fontSize: 11, color: textSecondary, flexShrink: 0 }}>{item.weight_pct.toFixed(1)}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}
