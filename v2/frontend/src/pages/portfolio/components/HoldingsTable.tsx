// Sortable, searchable holdings table matching the Ledger design
import { useState, useMemo } from 'react'
import { useTheme } from '@mui/material'
import type { Theme } from '@mui/material'
import { TickerGlyph, Spark, fmtEUR, fmtPct, seeded } from '../../../components/charts/design/DesignPrimitives'
import type { RawAsset } from '../../../presenters/portfolioPresenter'

interface HoldingsTableProps {
  rows: RawAsset[]
  search?: string
  sector?: string
}

type SortKey = 'ticker' | 'value' | 'pnl_pct' | 'weight_pct' | 'daily_value_return'

function makeSparkline(asset: RawAsset): number[] {
  const series = asset.price_series
  if (series && series.length > 1) return series.slice(-30)
  // deterministic fallback
  const r = seeded(asset.ticker.charCodeAt(0) * 31 + (asset.ticker.charCodeAt(1) || 7))
  const arr: number[] = []
  let v = 100
  for (let i = 0; i < 30; i++) { v *= 1 + (r() - 0.48) * 0.025; arr.push(v) }
  return arr
}

export default function HoldingsTable({ rows, search = '', sector = 'All' }: HoldingsTableProps) {
  const theme = useTheme()
  const [sort, setSort] = useState<{ key: SortKey; dir: 1 | -1 }>({ key: 'value', dir: -1 })

  const filtered = useMemo(() => {
    let r = rows
    if (sector !== 'All') {
      r = r.filter(a => (a.sector ?? a.tags?.[0] ?? '') === sector)
    }
    if (search) {
      const q = search.toLowerCase()
      r = r.filter(a => a.ticker.toLowerCase().includes(q) || a.name.toLowerCase().includes(q))
    }
    return [...r].sort((a, b) => {
      const av = a[sort.key], bv = b[sort.key]
      if (typeof av === 'string' && typeof bv === 'string') return av.localeCompare(bv) * sort.dir
      return ((Number(av) || 0) - (Number(bv) || 0)) * sort.dir
    })
  }, [rows, search, sort])

  const col = theme.palette.text.secondary
  const line = theme.palette.divider
  const hov = (theme as Theme & { custom: { bgRowHover: string } }).custom.bgRowHover

  const headers: { key: SortKey | null; label: string; w: number; align: 'left' | 'right' | 'center' }[] = [
    { key: 'ticker',              label: 'Ticker',  w: 130, align: 'left' },
    { key: null,                  label: 'Sector',  w: 100, align: 'left' },
    { key: 'value',               label: 'Value',   w: 100, align: 'right' },
    { key: 'pnl_pct',             label: 'Return',  w: 80,  align: 'right' },
    { key: null,                  label: '30D',     w: 90,  align: 'center' },
    { key: 'weight_pct',          label: 'Weight',  w: 110, align: 'left' },
    { key: 'daily_value_return',  label: 'Today',   w: 80,  align: 'right' },
  ]

  const gridCols = headers.map(h => h.w + 'px').join(' ')

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: 0, height: '100%' }}>
      {/* Header */}
      <div style={{
        display: 'grid', gridTemplateColumns: gridCols,
        padding: '10px 14px', borderBottom: `1px solid ${line}`,
        fontSize: 10.5, fontWeight: 600, letterSpacing: '.06em', textTransform: 'uppercase',
        color: col, background: theme.palette.background.paper,
        position: 'sticky', top: 0, zIndex: 1,
      }}>
        {headers.map(h => (
          <div key={h.label} style={{ textAlign: h.align, cursor: h.key ? 'pointer' : 'default', userSelect: 'none' }}
               onClick={() => h.key && setSort(s => ({ key: h.key!, dir: s.key === h.key ? (s.dir === -1 ? 1 : -1) : -1 }))}>
            {h.label}
            {h.key && sort.key === h.key && (
              <span style={{ marginLeft: 4, color: theme.palette.primary.main }}>{sort.dir < 0 ? '↓' : '↑'}</span>
            )}
          </div>
        ))}
      </div>

      {/* Rows */}
      <div style={{ flex: 1, overflowY: 'auto' }}>
        {filtered.map(asset => (
          <HoldingsRow key={asset.ticker} asset={asset} gridCols={gridCols} line={line} hov={hov} theme={theme} />
        ))}
      </div>
    </div>
  )
}

function HoldingsRow({ asset, gridCols, line, hov, theme }: {
  asset: RawAsset
  gridCols: string
  line: string
  hov: string
  theme: Theme
}) {
  const [hover, setHover] = useState(false)
  const value = Number(asset.value) || 0
  const pnlPct = Number(asset.pnl_pct) || 0
  const weight = Number(asset.weight_pct) || 0
  const dayRet = Number(asset.daily_value_return) || 0
  const spark = useMemo(() => makeSparkline(asset), [asset])
  const sector = asset.sector ?? asset.tags?.[0] ?? ''
  const upColor = theme.palette.success.main
  const dnColor = theme.palette.error.main

  return (
    <div
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        display: 'grid', gridTemplateColumns: gridCols,
        padding: '10px 14px', borderBottom: `1px solid ${line}`,
        fontSize: 12.5, alignItems: 'center', cursor: 'pointer',
        background: hover ? hov : 'transparent',
        transition: 'background .12s',
      }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
        <TickerGlyph ticker={asset.ticker} sector={sector} size={22} />
        <div style={{ display: 'flex', flexDirection: 'column', minWidth: 0 }}>
          <span style={{ fontWeight: 600, color: theme.palette.text.primary }}>{asset.ticker.toUpperCase()}</span>
          <span style={{ fontSize: 10.5, color: theme.palette.text.secondary, maxWidth: 90, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{asset.name}</span>
        </div>
      </div>
      <div style={{ fontSize: 11.5, color: theme.palette.text.secondary, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
        {sector || '—'}
      </div>
      <div style={{ textAlign: 'right', fontFamily: 'ui-monospace', fontVariantNumeric: 'tabular-nums', fontWeight: 600, color: theme.palette.text.primary }}>
        {fmtEUR(value, 0)}
      </div>
      <div style={{ textAlign: 'right', fontFamily: 'ui-monospace', fontVariantNumeric: 'tabular-nums', fontWeight: 600, color: pnlPct >= 0 ? upColor : dnColor }}>
        {fmtPct(pnlPct, 1)}
      </div>
      <div style={{ display: 'flex', justifyContent: 'center' }}>
        <Spark data={spark} w={70} h={20}
               color={pnlPct >= 0 ? upColor : dnColor} />
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div style={{ flex: 1, height: 4, background: theme.palette.mode === 'dark' ? '#1f1f24' : '#f4f1ec', borderRadius: 999, position: 'relative' }}>
          <div style={{ position: 'absolute', left: 0, top: 0, height: '100%', width: Math.min(weight * 4, 100) + '%', background: theme.palette.primary.main, borderRadius: 999, opacity: 0.7 }} />
        </div>
        <span style={{ fontSize: 11, color: theme.palette.text.secondary, fontFamily: 'ui-monospace', fontVariantNumeric: 'tabular-nums', minWidth: 36, textAlign: 'right' }}>{weight.toFixed(1)}%</span>
      </div>
      <div style={{ textAlign: 'right', fontFamily: 'ui-monospace', fontVariantNumeric: 'tabular-nums', fontWeight: 600, color: dayRet >= 0 ? upColor : dnColor }}>
        {dayRet !== 0 ? fmtPct(dayRet * 100, 2) : '—'}
      </div>
    </div>
  )
}
