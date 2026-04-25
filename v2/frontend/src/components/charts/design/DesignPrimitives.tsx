// Design primitives matching the Ledger design system:
// Delta pill, TickerGlyph, inline Spark SVG, seeded random

import { useTheme } from '@mui/material'

// ─── seeded random (deterministic per ticker) ──────────────────────────────
export function seeded(seed: number) {
  let s = seed | 0
  return () => {
    s = (s * 1664525 + 1013904223) | 0
    return ((s >>> 0) % 10000) / 10000
  }
}

// ─── formatting ────────────────────────────────────────────────────────────
export const fmtEUR = (n: number, frac = 2) =>
  new Intl.NumberFormat('en-IE', { style: 'currency', currency: 'EUR', minimumFractionDigits: frac, maximumFractionDigits: frac }).format(n)

export const fmtNum = (n: number, frac = 2) =>
  new Intl.NumberFormat('en-IE', { minimumFractionDigits: frac, maximumFractionDigits: frac }).format(n)

export const fmtPct = (n: number, frac = 2) =>
  (n >= 0 ? '+' : '') + n.toFixed(frac) + '%'

export const fmtCompact = (n: number) => {
  if (Math.abs(n) >= 1000) return '€' + (n / 1000).toFixed(1) + 'k'
  return '€' + n.toFixed(0)
}

// ─── sector palette ────────────────────────────────────────────────────────
export const SECTOR_PALETTE: Record<string, string> = {
  Tech:       'oklch(0.72 0.13 250)',
  ETF:        'oklch(0.7 0.1 200)',
  Energy:     'oklch(0.7 0.13 50)',
  Health:     'oklch(0.72 0.13 350)',
  Consumer:   'oklch(0.74 0.11 100)',
  Auto:       'oklch(0.7 0.14 30)',
  Industrial: 'oklch(0.7 0.1 280)',
  Financial:  'oklch(0.72 0.12 160)',
  Bond:       'oklch(0.72 0.07 300)',
}

export function sectorColor(sector: string) {
  return SECTOR_PALETTE[sector] ?? 'oklch(0.7 0.06 240)'
}

// ─── Delta pill ────────────────────────────────────────────────────────────
interface DeltaProps {
  value: number
  suffix?: string
  size?: 'sm' | 'md'
}

export function Delta({ value, suffix = '%', size = 'md' }: DeltaProps) {
  const theme = useTheme()
  const up = value >= 0
  const sz = size === 'sm' ? { font: 11, pad: '2px 6px' } : { font: 12.5, pad: '3px 8px' }
  const color = up ? theme.palette.success.main : theme.palette.error.main
  const bg = up
    ? theme.palette.mode === 'dark' ? 'rgba(74, 222, 128, 0.15)' : 'rgba(22, 163, 74, 0.1)'
    : theme.palette.mode === 'dark' ? 'rgba(248, 113, 113, 0.15)' : 'rgba(220, 38, 38, 0.1)'
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 3,
      fontSize: sz.font, fontWeight: 600, fontVariantNumeric: 'tabular-nums',
      color, background: bg,
      padding: sz.pad, borderRadius: 999,
      letterSpacing: '-0.01em',
      whiteSpace: 'nowrap',
    }}>
      <span style={{ fontSize: sz.font - 2, lineHeight: 1 }}>{up ? '▲' : '▼'}</span>
      {Math.abs(value).toFixed(2)}{suffix}
    </span>
  )
}

// ─── TickerGlyph ────────────────────────────────────────────────────────────
interface TickerGlyphProps {
  ticker: string
  sector?: string
  size?: number
}

export function TickerGlyph({ ticker, sector = '', size = 26 }: TickerGlyphProps) {
  const c = sectorColor(sector)
  return (
    <div style={{
      width: size, height: size, borderRadius: size * 0.3,
      background: c, color: '#fff',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontSize: size * 0.4, fontWeight: 700, letterSpacing: '-0.02em',
      flexShrink: 0,
    }}>
      {ticker.slice(0, 2).toUpperCase()}
    </div>
  )
}

// ─── Inline SVG sparkline ───────────────────────────────────────────────────
interface SparkProps {
  data: number[]
  color?: string
  w?: number
  h?: number
  fill?: boolean
  strokeW?: number
}

export function Spark({ data, color, w = 80, h = 24, fill = false, strokeW = 1.4 }: SparkProps) {
  if (!data || !data.length) return null
  const min = Math.min(...data), max = Math.max(...data)
  const span = (max - min) || 1
  const pts: [number, number][] = data.map((v, i) => [
    (i / (data.length - 1)) * w,
    h - ((v - min) / span) * h,
  ])
  const path = pts.map(([x, y], i) => (i ? 'L' : 'M') + x.toFixed(1) + ' ' + y.toFixed(1)).join(' ')
  const area = path + ` L ${w} ${h} L 0 ${h} Z`
  const trendUp = data[data.length - 1] >= data[0]
  const c = color ?? (trendUp ? 'var(--spark-up, #16a34a)' : 'var(--spark-dn, #dc2626)')
  return (
    <svg width={w} height={h} style={{ display: 'block' }}>
      {fill && <path d={area} fill={c} opacity={0.12} />}
      <path d={path} stroke={c} fill="none" strokeWidth={strokeW} strokeLinejoin="round" strokeLinecap="round" />
    </svg>
  )
}
