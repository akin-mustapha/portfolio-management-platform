// Responsive area chart with hover scrubber, matching the design's ValueChart.
import { useRef, useState, useMemo, useEffect } from 'react'
import { useTheme } from '@mui/material'
import type { Theme } from '@mui/material'
import { fmtEUR, fmtNum, fmtPct } from './DesignPrimitives'

export interface SeriesPoint { d: number; v: number; inv: number }

interface ValueChartProps {
  series: SeriesPoint[]
  range?: string
  height?: number
  showInvested?: boolean
}

const RANGE_DAYS: Record<string, number> = { '1W': 7, '1M': 30, '3M': 90, '6M': 180, '1Y': 365, ALL: 9999 }

export default function ValueChart({ series, range = '6M', height = 200, showInvested = true }: ValueChartProps) {
  const theme = useTheme()
  const ref = useRef<HTMLDivElement>(null)
  const [hover, setHover] = useState<{ idx: number; x: number; y: number; v: number } | null>(null)
  const [w, setW] = useState(800)

  useEffect(() => {
    if (!ref.current) return
    const ro = new ResizeObserver(([e]) => setW(e.contentRect.width))
    ro.observe(ref.current)
    return () => ro.disconnect()
  }, [])

  const slice = useMemo(() => {
    const n = series.length
    const days = RANGE_DAYS[range] ?? n
    return series.slice(Math.max(0, n - days))
  }, [series, range])

  const padL = 0, padR = 0, padT = 12, padB = 22
  const innerW = Math.max(0, w - padL - padR)
  const innerH = height - padT - padB
  const vals = slice.map(d => d.v)
  const min = Math.min(...vals) * 0.985
  const max = Math.max(...vals) * 1.005
  const span = max - min || 1
  const xPos = (i: number) => padL + (i / (slice.length - 1)) * innerW
  const yPos = (v: number) => padT + (1 - (v - min) / span) * innerH

  const linePath = slice.map((d, i) => (i ? 'L' : 'M') + xPos(i).toFixed(1) + ' ' + yPos(d.v).toFixed(1)).join(' ')
  const areaPath = linePath + ` L ${xPos(slice.length - 1)} ${padT + innerH} L ${xPos(0)} ${padT + innerH} Z`
  const accent = theme.palette.primary.main
  const gradId = `vcgrad-${range}`

  const onMove = (e: React.MouseEvent) => {
    if (!ref.current) return
    const rect = ref.current.getBoundingClientRect()
    const px = e.clientX - rect.left
    const idx = Math.max(0, Math.min(slice.length - 1, Math.round(((px - padL) / innerW) * (slice.length - 1))))
    setHover({ idx, x: xPos(idx), y: yPos(slice[idx].v), v: slice[idx].v })
  }

  const today = new Date(2026, 3, 25)
  const labelDate = (i: number) => {
    const d = new Date(today)
    d.setDate(d.getDate() - (slice.length - 1 - i))
    return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' })
  }

  return (
    <div ref={ref} style={{ position: 'relative', width: '100%' }}
         onMouseMove={onMove} onMouseLeave={() => setHover(null)}>
      <svg width={w} height={height} style={{ display: 'block' }}>
        <defs>
          <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={accent} stopOpacity="0.28" />
            <stop offset="100%" stopColor={accent} stopOpacity="0" />
          </linearGradient>
        </defs>

        {showInvested && slice.length > 0 && (() => {
          const invY = padT + innerH * 0.55
          return (
            <>
              <line x1={padL} x2={padL + innerW} y1={invY} y2={invY}
                    stroke={theme.palette.divider} strokeDasharray="3 4" strokeWidth="1" />
              <text x={padL + innerW - 4} y={invY - 4} textAnchor="end"
                    fontSize="10" fill={theme.palette.text.secondary} fontFamily="ui-monospace,monospace">
                invested {fmtEUR(slice[0].inv, 0)}
              </text>
            </>
          )
        })()}

        <path d={areaPath} fill={`url(#${gradId})`} />
        <path d={linePath} fill="none" stroke={accent} strokeWidth="1.75" strokeLinejoin="round" />

        {hover && (
          <>
            <line x1={hover.x} x2={hover.x} y1={padT} y2={padT + innerH}
                  stroke={theme.palette.divider} strokeWidth="1" />
            <circle cx={hover.x} cy={hover.y} r="4"
                    fill={theme.palette.background.paper} stroke={accent} strokeWidth="1.75" />
          </>
        )}

        {[0, 0.25, 0.5, 0.75, 1].map(t => {
          const i = Math.floor(t * (slice.length - 1))
          return (
            <text key={t} x={xPos(i)} y={height - 4} textAnchor="middle"
                  fontSize="10" fill={theme.palette.text.secondary} fontFamily="ui-monospace,monospace">
              {labelDate(i)}
            </text>
          )
        })}
      </svg>

      {hover && (
        <div style={{
          position: 'absolute',
          left: Math.min(Math.max(hover.x + 10, 8), w - 140),
          top: 8,
          background: theme.palette.background.paper,
          border: `1px solid ${theme.palette.divider}`,
          borderRadius: 8, padding: '6px 10px', fontSize: 11.5,
          boxShadow: (theme as Theme & { custom: { shadowPop: string } }).custom.shadowPop,
          pointerEvents: 'none', minWidth: 120,
          fontVariantNumeric: 'tabular-nums',
          color: theme.palette.text.primary,
        }}>
          <div style={{ color: theme.palette.text.secondary, fontSize: 10, textTransform: 'uppercase', letterSpacing: '.06em' }}>
            {labelDate(hover.idx)}
          </div>
          <div style={{ fontWeight: 600, fontSize: 14, marginTop: 2 }}>{fmtEUR(hover.v)}</div>
          {slice.length > 0 && (
            <div style={{ color: theme.palette.success.main, fontSize: 11 }}>
              {fmtPct(((hover.v - slice[0].inv) / slice[0].inv) * 100)} vs invested
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// Range selector button strip
interface RangeSelectorProps {
  range: string
  onChange: (r: string) => void
}

export function RangeSelector({ range, onChange }: RangeSelectorProps) {
  const theme = useTheme()
  return (
    <div style={{ display: 'flex', gap: 4, marginTop: 12 }}>
      {['1W', '1M', '3M', '6M', '1Y', 'ALL'].map(r => (
        <button key={r} onClick={() => onChange(r)} style={{
          padding: '5px 12px', fontSize: 11.5, fontWeight: 600, fontFamily: 'ui-monospace',
          border: `1px solid ${range === r ? theme.palette.primary.main : theme.palette.divider}`,
          background: range === r ? theme.palette.primary.main + '18' : 'transparent',
          color: range === r ? theme.palette.primary.main : theme.palette.text.secondary,
          borderRadius: 6, cursor: 'pointer',
        }}>{r}</button>
      ))}
    </div>
  )
}

export { fmtNum }
