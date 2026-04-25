// Daily returns heatmap — top 14 holdings by value, last 14 days
import { useTheme } from '@mui/material'
import { fmtPct } from './DesignPrimitives'

export interface HeatmapRow {
  ticker: string
  value: number
  daily14: number[]
}

interface HeatmapProps {
  items: HeatmapRow[]
  days?: number
  cell?: number
}

function heatColor(v: number) {
  const intensity = Math.min(1, Math.abs(v) / 2)
  if (v >= 0) return `oklch(${0.97 - intensity * 0.25} ${0.04 + intensity * 0.1} 152)`
  return `oklch(${0.97 - intensity * 0.25} ${0.04 + intensity * 0.1} 25)`
}

export default function HeatmapChart({ items, days = 14, cell = 22 }: HeatmapProps) {
  const theme = useTheme()
  const sorted = [...items].sort((a, b) => b.value - a.value).slice(0, 14)
  const today = new Date(2026, 3, 25)
  const dates = Array.from({ length: days }, (_, i) => {
    const d = new Date(today)
    d.setDate(d.getDate() - (days - 1 - i))
    return d
  })

  return (
    <div style={{ display: 'flex', flexDirection: 'column', fontFamily: 'ui-monospace', fontSize: 10.5, overflowX: 'auto' }}>
      <div style={{ display: 'grid', gridTemplateColumns: `70px repeat(${days}, ${cell}px)`, gap: 3, marginBottom: 6 }}>
        <div />
        {dates.map((d, i) => (
          <div key={i} style={{ textAlign: 'center', color: theme.palette.text.secondary, fontSize: 9.5 }}>
            {i % 2 === 0 ? d.getDate() : ''}
          </div>
        ))}
      </div>
      {sorted.map(h => (
        <div key={h.ticker} style={{ display: 'grid', gridTemplateColumns: `70px repeat(${days}, ${cell}px)`, gap: 3, marginBottom: 3, alignItems: 'center' }}>
          <div style={{ fontWeight: 600, fontSize: 11, color: theme.palette.text.primary }}>
            {h.ticker.toUpperCase().slice(0, 6)}
          </div>
          {(h.daily14 ?? []).slice(0, days).map((v, i) => (
            <div key={i}
                 title={`${dates[i]?.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' })}: ${fmtPct(v, 2)}`}
                 style={{
                   width: cell, height: cell, borderRadius: 3,
                   background: heatColor(v),
                   border: i === days - 1 ? `1px solid ${theme.palette.text.primary}` : 'none',
                 }} />
          ))}
        </div>
      ))}
    </div>
  )
}
