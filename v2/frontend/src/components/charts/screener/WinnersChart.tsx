import { useTheme } from '@mui/material'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { fmtNum } from '../../../utils/chartUtils'

interface WinnerItem {
  ticker: string
  profit: number
  label: string
  name: string
}

interface WinnersChartProps {
  winners?: WinnerItem[]
}

export default function WinnersChart({ winners }: WinnersChartProps) {
  const theme = useTheme()
  if (!winners?.length) return null

  function CustomTooltip({ active, payload }: { active?: boolean; payload?: unknown[] }) {
    if (!active || !payload?.length) return null
    const d = (payload as Array<{ payload: WinnerItem }>)[0].payload
    return (
      <div style={{ background: theme.palette.background.paper, border: `1px solid ${theme.palette.divider}`, padding: '6px 10px', fontSize: 11, borderRadius: 4 }}>
        <div style={{ fontWeight: 600 }}>{d.ticker}</div>
        <div style={{ color: theme.palette.text.secondary, fontSize: 10, marginBottom: 2 }}>{d.name}</div>
        <div>Profit: {fmtNum(d.profit)}</div>
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={winners} layout="vertical" margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
        <XAxis type="number" tick={{ fontSize: 10 }} tickLine={false} />
        <YAxis type="category" dataKey="label" tick={{ fontSize: 10 }} width={60} />
        <Tooltip content={<CustomTooltip />} cursor={{ fill: theme.palette.action.hover }} />
        <Bar dataKey="profit" radius={[0, 3, 3, 0]}>
          {winners.map((_, i) => (
            <Cell key={i} fill={theme.palette.success.main} opacity={1 - i * 0.06} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
