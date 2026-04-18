import { useTheme } from '@mui/material'
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  ReferenceLine,
  Cell,
  Label,
} from 'recharts'
import { fmtNum } from '../../utils/chartUtils'

interface OpportunitiesChartProps {
  /** position_distribution from presenter */
  distribution?: Array<{
    ticker: string
    weight_pct: number
    roi_pct: number
    profit: number
    value: number
    name: string
  }>
}

type DistributionItem = NonNullable<OpportunitiesChartProps['distribution']>[number]

export default function OpportunitiesChart({ distribution }: OpportunitiesChartProps) {
  const theme = useTheme()

  if (!distribution?.length) return null

  const avgWeight = distribution.reduce((s, d) => s + d.weight_pct, 0) / distribution.length

  function CustomTooltip({ active, payload }: { active?: boolean; payload?: unknown[] }) {
    if (!active || !payload?.length) return null
    const d = (payload as Array<{ payload: DistributionItem }>)[0].payload
    return (
      <div style={{ background: theme.palette.background.paper, border: `1px solid ${theme.palette.divider}`, padding: '6px 10px', fontSize: 11, borderRadius: 4 }}>
        <div style={{ fontWeight: 600 }}>{d.ticker}</div>
        <div style={{ color: theme.palette.text.secondary, fontSize: 10, marginBottom: 2 }}>{d.name}</div>
        <div>Weight: {d.weight_pct.toFixed(1)}%</div>
        <div>ROI: {d.roi_pct > 0 ? '+' : ''}{d.roi_pct.toFixed(2)}%</div>
        <div>P&L: {fmtNum(d.profit)}</div>
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <ScatterChart margin={{ top: 12, right: 16, bottom: 24, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
        <XAxis
          type="number"
          dataKey="weight_pct"
          name="Weight"
          tick={{ fontSize: 10 }}
          tickLine={false}
          unit="%"
        >
          <Label value="Portfolio Weight %" position="insideBottom" offset={-12} style={{ fontSize: 10, fill: theme.palette.text.secondary }} />
        </XAxis>
        <YAxis
          type="number"
          dataKey="roi_pct"
          name="ROI"
          tick={{ fontSize: 10 }}
          tickLine={false}
          width={52}
          unit="%"
        />
        <Tooltip content={<CustomTooltip />} />
        {/* quadrant lines */}
        <ReferenceLine y={0} stroke={theme.palette.divider} strokeDasharray="4 2" />
        <ReferenceLine x={avgWeight} stroke={theme.palette.divider} strokeDasharray="4 2" />
        <Scatter data={distribution} name="Positions">
          {distribution.map((d) => (
            <Cell
              key={d.ticker}
              fill={d.roi_pct >= 0 ? theme.palette.success.main : theme.palette.error.main}
              opacity={0.85}
              r={Math.max(5, Math.min(14, Math.sqrt(Math.abs(d.value)) / 10))}
            />
          ))}
        </Scatter>
      </ScatterChart>
    </ResponsiveContainer>
  )
}
