import { useTheme } from '@mui/material'
import type { Theme } from '@mui/material'
import { usePortfolioContext } from '../PortfolioContext'
import { TickerGlyph, fmtEUR, fmtPct } from '../../../components/charts/design/DesignPrimitives'
import type { RawAsset } from '../../../presenters/portfolioPresenter'

// ─── Shared card shell ────────────────────────────────────────────────────

function pillBtn(primary: boolean | undefined, theme: Theme) {
  return {
    padding: '6px 12px', fontSize: 11.5, fontWeight: 600,
    border: `1px solid ${primary ? theme.palette.primary.main : theme.palette.divider}`,
    background: primary ? theme.palette.primary.main : theme.palette.background.paper,
    color: primary ? '#fff' : theme.palette.text.primary,
    borderRadius: 7, cursor: 'pointer', whiteSpace: 'nowrap' as const,
  }
}

interface CardShellProps {
  title: string
  sub?: string
  badge?: string
  badgeColor?: string
  action?: React.ReactNode
  children?: React.ReactNode
}

function CardShell({ title, sub, badge, badgeColor, action, children }: CardShellProps) {
  const theme = useTheme()
  return (
    <div style={{
      border: `1px solid ${theme.palette.divider}`, borderRadius: 14,
      background: theme.palette.background.paper, padding: '18px 22px',
      display: 'flex', flexDirection: 'column', gap: 14, minWidth: 0,
    }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6, minWidth: 0 }}>
        {badge && (
          <span style={{
            alignSelf: 'flex-start', fontSize: 9.5, fontWeight: 700, letterSpacing: '.08em',
            textTransform: 'uppercase', padding: '2px 8px', borderRadius: 999,
            background: badgeColor ?? (theme.palette.primary.main + '20'),
            color: badgeColor ? theme.palette.text.primary : theme.palette.primary.main,
          }}>{badge}</span>
        )}
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 10, minWidth: 0 }}>
          <div style={{ minWidth: 0, flex: 1 }}>
            <div style={{ fontSize: 14.5, fontWeight: 600, lineHeight: 1.3, color: theme.palette.text.primary }}>{title}</div>
            {sub && <div style={{ fontSize: 11.5, color: theme.palette.text.secondary, marginTop: 4, lineHeight: 1.4 }}>{sub}</div>}
          </div>
          {action && <div style={{ flexShrink: 0 }}>{action}</div>}
        </div>
      </div>
      {children}
    </div>
  )
}

// ─── 1. Rebalance ─────────────────────────────────────────────────────────

const TARGET_WEIGHTS: Record<string, number> = {
  Tech: 0.30, ETF: 0.30, Energy: 0.10, Health: 0.05,
  Consumer: 0.07, Auto: 0.05, Industrial: 0.05, Financial: 0.04, Bond: 0.04,
}

function Rebalance({ assets, portfolioValue }: { assets: RawAsset[]; portfolioValue: number }) {
  const theme = useTheme()
  const totalValue = assets.reduce((s, a) => s + (Number(a.value) || 0), 0)
  const current: Record<string, number> = {}
  assets.forEach(a => {
    const sector = (a as Record<string, unknown>).sector as string ?? a.tags?.[0] ?? 'Other'
    current[sector] = (current[sector] ?? 0) + (Number(a.value) || 0) / (totalValue || 1)
  })
  const rows = Object.keys(TARGET_WEIGHTS).map(s => ({
    sector: s, current: current[s] ?? 0, target: TARGET_WEIGHTS[s],
    delta: (current[s] ?? 0) - TARGET_WEIGHTS[s],
  })).sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta)).slice(0, 5)

  return (
    <CardShell badge="Rebalance" badgeColor="oklch(0.92 0.06 250 / 0.6)"
               title="Drift from target weights"
               sub="Tech is overweight. Consider trimming and topping up Health & Bonds."
               action={<button style={pillBtn(true, theme)}>Plan</button>}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {rows.map(r => (
          <div key={r.sector}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 4 }}>
              <span style={{ fontWeight: 600, color: theme.palette.text.primary }}>{r.sector}</span>
              <span style={{ fontFamily: 'ui-monospace', fontVariantNumeric: 'tabular-nums' }}>
                <span style={{ color: theme.palette.text.secondary }}>{(r.current * 100).toFixed(1)}%</span>
                <span style={{ color: theme.palette.text.secondary, margin: '0 6px' }}>→</span>
                <span style={{ color: theme.palette.text.primary }}>{(r.target * 100).toFixed(1)}%</span>
                <span style={{ marginLeft: 10, fontWeight: 600, color: r.delta > 0 ? theme.palette.error.main : theme.palette.success.main }}>
                  {r.delta > 0 ? 'trim ' : 'add '}{fmtEUR(Math.abs(r.delta) * portfolioValue, 0)}
                </span>
              </span>
            </div>
            <div style={{ position: 'relative', height: 6, background: theme.palette.mode === 'dark' ? '#1f1f24' : '#f4f1ec', borderRadius: 3 }}>
              <div style={{ position: 'absolute', left: (r.target * 100) + '%', top: -2, bottom: -2, width: 1, background: theme.palette.text.secondary, opacity: 0.5 }} />
              <div style={{
                position: 'absolute', top: 0, height: '100%',
                left: Math.min(r.current, r.target) * 100 + '%',
                width: Math.abs(r.delta) * 100 + '%',
                background: r.delta > 0 ? theme.palette.error.main : theme.palette.success.main,
                opacity: 0.7, borderRadius: 3,
              }} />
            </div>
          </div>
        ))}
      </div>
    </CardShell>
  )
}

// ─── 2. Tax-loss harvesting ───────────────────────────────────────────────

function TaxLoss({ assets }: { assets: RawAsset[] }) {
  const theme = useTheme()
  const losers = [...assets]
    .filter(a => (Number(a.profit) || 0) < 0)
    .sort((a, b) => (Number(a.profit) || 0) - (Number(b.profit) || 0))
    .slice(0, 4)
  const totalLoss = losers.reduce((s, a) => s + (Number(a.profit) || 0), 0)
  const taxSaving = Math.abs(totalLoss) * 0.26

  return (
    <CardShell badge="Tax-loss" badgeColor="oklch(0.92 0.07 80 / 0.6)"
               title="Harvest before year-end"
               sub={`Realize ${fmtEUR(Math.abs(totalLoss), 0)} in losses to save ~${fmtEUR(taxSaving, 0)} in taxes`}
               action={<button style={pillBtn(false, theme)}>Plan</button>}>
      <div>
        {losers.map(a => {
          const pnlPct = Number(a.pnl_pct) || 0
          const pl = Number(a.profit) || 0
          const sector = (a as Record<string, unknown>).sector as string ?? a.tags?.[0] ?? ''
          return (
            <div key={a.ticker} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '6px 0', borderBottom: `1px solid ${theme.palette.mode === 'dark' ? '#1f1f24' : '#f4f1ec'}` }}>
              <TickerGlyph ticker={a.ticker} sector={sector} size={20} />
              <span style={{ fontWeight: 600, fontSize: 12, minWidth: 56, color: theme.palette.text.primary }}>{a.ticker.toUpperCase()}</span>
              <span style={{ flex: 1, fontSize: 11, color: theme.palette.text.secondary, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{a.name}</span>
              <span style={{ fontFamily: 'ui-monospace', fontSize: 11.5, color: theme.palette.error.main, fontWeight: 600 }}>{fmtEUR(pl, 0)}</span>
              <span style={{ fontFamily: 'ui-monospace', fontSize: 10.5, color: theme.palette.text.secondary, minWidth: 50, textAlign: 'right' }}>{fmtPct(pnlPct, 1)}</span>
            </div>
          )
        })}
      </div>
    </CardShell>
  )
}

// ─── 3. Cash deployment ──────────────────────────────────────────────────

const CASH_IDEAS = [
  { ticker: 'VHYL', name: 'Vanguard High Dividend Yield', why: 'Diversifies away from tech', alloc: 400 },
  { ticker: 'IWDA', name: 'iShares Core MSCI World',      why: 'Broad ex-US exposure',      alloc: 500 },
  { ticker: 'XEON', name: 'Xtrackers Eurozone Gov Bond',  why: 'Ballast vs equity drawdown', alloc: 240 },
]

function CashDeploy({ cash }: { cash: number }) {
  const theme = useTheme()
  return (
    <CardShell badge="Deploy cash" badgeColor="oklch(0.92 0.06 152 / 0.6)"
               title={`${fmtEUR(cash)} idle`}
               sub="Aligned to underweight sectors and your risk profile"
               action={<button style={pillBtn(true, theme)}>Trade</button>}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {CASH_IDEAS.map(i => (
          <div key={i.ticker} style={{ display: 'grid', gridTemplateColumns: '24px 1fr auto', gap: 10, alignItems: 'center', padding: '6px 0', borderBottom: `1px solid ${theme.palette.mode === 'dark' ? '#1f1f24' : '#f4f1ec'}` }}>
            <div style={{ width: 24, height: 24, borderRadius: 6, background: 'oklch(0.85 0.05 200)', color: theme.palette.text.primary, display: 'grid', placeItems: 'center', fontSize: 9.5, fontWeight: 700 }}>{i.ticker.slice(0, 2)}</div>
            <div>
              <div style={{ display: 'flex', gap: 8, alignItems: 'baseline' }}>
                <span style={{ fontWeight: 600, fontSize: 12, color: theme.palette.text.primary }}>{i.ticker}</span>
                <span style={{ fontSize: 11, color: theme.palette.text.secondary }}>{i.name}</span>
              </div>
              <div style={{ fontSize: 10.5, color: theme.palette.text.secondary, marginTop: 1 }}>{i.why}</div>
            </div>
            <span style={{ fontFamily: 'ui-monospace', fontSize: 12, fontWeight: 600, color: theme.palette.text.primary }}>{fmtEUR(i.alloc, 0)}</span>
          </div>
        ))}
      </div>
    </CardShell>
  )
}

// ─── 4. Dividend calendar ─────────────────────────────────────────────────

const DIVIDENDS = [
  { ticker: 'AAPL', date: 'May  9', perShare: 0.25, qty: 3 },
  { ticker: 'PFE',  date: 'May 12', perShare: 0.42, qty: 22 },
  { ticker: 'KO',   date: 'May 16', perShare: 0.49, qty: 14 },
  { ticker: 'NKE',  date: 'Jun  2', perShare: 0.40, qty: 8 },
]

function DividendCalendar({ assets }: { assets: RawAsset[] }) {
  const theme = useTheme()
  const total = DIVIDENDS.reduce((s, e) => s + e.perShare * e.qty, 0)
  return (
    <CardShell badge="Dividends" badgeColor="oklch(0.92 0.06 152 / 0.6)"
               title="Upcoming ex-dividend dates"
               sub={`Estimated next 6 weeks · ${fmtEUR(total, 0)} expected`}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
        {DIVIDENDS.map(e => {
          const asset = assets.find(a => a.ticker === e.ticker)
          const sector = asset ? ((asset as Record<string, unknown>).sector as string ?? asset.tags?.[0] ?? '') : 'Tech'
          return (
            <div key={e.ticker} style={{ display: 'grid', gridTemplateColumns: '20px 1fr auto', gap: 8, alignItems: 'center', padding: '6px 8px', background: theme.palette.mode === 'dark' ? '#1f1f24' : '#f4f1ec', borderRadius: 7 }}>
              <TickerGlyph ticker={e.ticker} sector={sector} size={20} />
              <div style={{ minWidth: 0 }}>
                <div style={{ fontSize: 11.5, fontWeight: 600, color: theme.palette.text.primary }}>{e.ticker}</div>
                <div style={{ fontSize: 10, color: theme.palette.text.secondary, fontFamily: 'ui-monospace' }}>{e.date} · €{e.perShare.toFixed(2)}/sh</div>
              </div>
              <span style={{ fontFamily: 'ui-monospace', fontSize: 11.5, fontWeight: 600, color: theme.palette.success.main }}>+{fmtEUR(e.perShare * e.qty, 2)}</span>
            </div>
          )
        })}
      </div>
    </CardShell>
  )
}

// ─── 5. Earnings watchlist ────────────────────────────────────────────────

const EARNINGS = [
  { ticker: 'AAPL', date: 'Apr 30', est: '$1.50', prev: '+8% yoy' },
  { ticker: 'META', date: 'May  1', est: '$5.20', prev: '+12% yoy' },
  { ticker: 'TSLA', date: 'May  3', est: '$0.42', prev: '−18% yoy' },
  { ticker: 'NVDA', date: 'May  8', est: '$0.91', prev: '+22% yoy' },
  { ticker: 'PLTR', date: 'May  9', est: '$0.11', prev: '+30% yoy' },
]

function Earnings({ assets }: { assets: RawAsset[] }) {
  const theme = useTheme()
  return (
    <CardShell badge="Earnings" badgeColor="oklch(0.92 0.06 60 / 0.6)"
               title="Reporting next 2 weeks"
               sub="Holdings reporting · consensus estimates">
      <div>
        {EARNINGS.map(e => {
          const asset = assets.find(a => a.ticker === e.ticker)
          const sector = asset ? ((asset as Record<string, unknown>).sector as string ?? asset.tags?.[0] ?? '') : 'Tech'
          return (
            <div key={e.ticker} style={{ display: 'grid', gridTemplateColumns: '24px 60px 1fr auto', gap: 10, padding: '8px 0', borderBottom: `1px solid ${theme.palette.mode === 'dark' ? '#1f1f24' : '#f4f1ec'}`, alignItems: 'center', fontSize: 12 }}>
              <TickerGlyph ticker={e.ticker} sector={sector} size={20} />
              <span style={{ fontFamily: 'ui-monospace', fontSize: 11, color: theme.palette.text.secondary }}>{e.date}</span>
              <span style={{ fontWeight: 600, color: theme.palette.text.primary }}>{e.ticker}</span>
              <span style={{ fontFamily: 'ui-monospace', fontSize: 11.5 }}>
                <span style={{ color: theme.palette.text.secondary }}>EPS </span>
                <span style={{ fontWeight: 600, color: theme.palette.text.primary }}>{e.est}</span>
                <span style={{ color: theme.palette.text.secondary, marginLeft: 8 }}>{e.prev}</span>
              </span>
            </div>
          )
        })}
      </div>
    </CardShell>
  )
}

// ─── 6. Concentration warnings ────────────────────────────────────────────

function ConcentrationWarn({ assets, portfolioValue }: { assets: RawAsset[]; portfolioValue: number }) {
  const theme = useTheme()
  const totalValue = assets.reduce((s, a) => s + (Number(a.value) || 0), 0)
  const heavy = [...assets]
    .map(a => ({ ...a, w: (Number(a.value) || 0) / (totalValue || 1) }))
    .sort((a, b) => b.w - a.w).slice(0, 3).filter(a => a.w > 0.05)

  return (
    <CardShell badge="Risk alert" badgeColor="oklch(0.92 0.08 25 / 0.6)"
               title="Single-name concentration"
               sub="Positions over 5% of portfolio carry idiosyncratic risk">
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {heavy.map(a => {
          const sector = (a as Record<string, unknown>).sector as string ?? a.tags?.[0] ?? ''
          return (
            <div key={a.ticker} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '8px 10px', background: theme.palette.mode === 'dark' ? '#1f1f24' : '#f4f1ec', borderRadius: 8 }}>
              <TickerGlyph ticker={a.ticker} sector={sector} size={28} />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 12.5, fontWeight: 600, color: theme.palette.text.primary }}>
                  {a.ticker.toUpperCase()} <span style={{ color: theme.palette.text.secondary, fontWeight: 400 }}>· {a.name}</span>
                </div>
                <div style={{ fontSize: 11, color: theme.palette.text.secondary, marginTop: 2 }}>
                  <span style={{ color: theme.palette.error.main, fontWeight: 600, fontFamily: 'ui-monospace' }}>{(a.w * 100).toFixed(1)}%</span>
                  {' '}weight · suggest trim to 5% (≈ {fmtEUR((a.w - 0.05) * portfolioValue, 0)})
                </div>
              </div>
              <button style={pillBtn(false, theme)}>Trim</button>
            </div>
          )
        })}
      </div>
    </CardShell>
  )
}

// ─── 7. Sector gaps ──────────────────────────────────────────────────────

const BENCHMARK: Record<string, number> = { Tech: 0.28, Health: 0.13, Financial: 0.13, Consumer: 0.10, Industrial: 0.09, Energy: 0.05, Auto: 0.03 }

function SectorGaps({ assets }: { assets: RawAsset[] }) {
  const theme = useTheme()
  const totalValue = assets.reduce((s, a) => s + (Number(a.value) || 0), 0)
  const current: Record<string, number> = {}
  assets.forEach(a => {
    const sector = (a as Record<string, unknown>).sector as string ?? a.tags?.[0] ?? 'Other'
    current[sector] = (current[sector] ?? 0) + (Number(a.value) || 0) / (totalValue || 1)
  })
  const rows = Object.keys(BENCHMARK).map(s => ({
    sector: s, you: current[s] ?? 0, bm: BENCHMARK[s], gap: (current[s] ?? 0) - BENCHMARK[s],
  }))

  return (
    <CardShell badge="Gaps" badgeColor="oklch(0.92 0.05 200 / 0.6)"
               title="Sector exposure vs MSCI World"
               sub="Underweights are opportunities; overweights are concentration">
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {rows.map(r => (
          <div key={r.sector} style={{ display: 'grid', gridTemplateColumns: '90px 1fr 70px', alignItems: 'center', gap: 10, fontSize: 11.5 }}>
            <span style={{ color: theme.palette.text.primary }}>{r.sector}</span>
            <div style={{ position: 'relative', height: 14, background: theme.palette.mode === 'dark' ? '#1f1f24' : '#f4f1ec', borderRadius: 3 }}>
              <div style={{ position: 'absolute', left: (r.bm * 200) + '%', top: -2, bottom: -2, width: 2, background: theme.palette.text.secondary, opacity: 0.5 }} />
              <div style={{ position: 'absolute', top: 0, height: '100%', left: 0, width: Math.min(r.you * 200, 100) + '%', background: r.gap < 0 ? 'oklch(0.78 0.12 200)' : 'oklch(0.78 0.13 30)', opacity: 0.7, borderRadius: 3 }} />
            </div>
            <span style={{ fontFamily: 'ui-monospace', textAlign: 'right', color: r.gap < 0 ? theme.palette.success.main : theme.palette.text.secondary, fontWeight: 600 }}>
              {r.gap >= 0 ? '+' : ''}{(r.gap * 100).toFixed(1)}pp
            </span>
          </div>
        ))}
      </div>
    </CardShell>
  )
}

// ─── 8. Similar to winners ────────────────────────────────────────────────

const SIMILAR_PICKS = [
  { ticker: 'AMD',  name: 'Advanced Micro Devices', because: 'Semi peer of NVDA / ASML', perf: 18.4 },
  { ticker: 'AMAT', name: 'Applied Materials',      because: 'Semi peer to ASML',        perf: 12.1 },
  { ticker: 'CRWD', name: 'CrowdStrike',            because: 'Cyber (complements ETFs)',  perf: 24.0 },
  { ticker: 'NOW',  name: 'ServiceNow',             because: 'Enterprise software',       perf: 9.8 },
]

function SimilarPicks() {
  const theme = useTheme()
  return (
    <CardShell badge="Discover" badgeColor="oklch(0.92 0.05 280 / 0.6)"
               title="Similar to your winners"
               sub="Peers of your top performers · click for deep dive">
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
        {SIMILAR_PICKS.map(p => (
          <div key={p.ticker} style={{ padding: 10, border: `1px solid ${theme.palette.divider}`, borderRadius: 8, cursor: 'pointer' }}>
            <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
              <span style={{ fontWeight: 600, fontSize: 12, color: theme.palette.text.primary }}>{p.ticker}</span>
              <span style={{ fontFamily: 'ui-monospace', fontSize: 11, color: theme.palette.success.main, fontWeight: 600 }}>+{p.perf.toFixed(1)}% YTD</span>
            </div>
            <div style={{ fontSize: 11, color: theme.palette.text.secondary, marginTop: 2 }}>{p.name}</div>
            <div style={{ fontSize: 10.5, color: theme.palette.primary.main, marginTop: 4 }}>{p.because}</div>
          </div>
        ))}
      </div>
    </CardShell>
  )
}

// ─── Page ─────────────────────────────────────────────────────────────────

export default function OpportunitiesTab() {
  const { summary } = usePortfolioContext()
  const theme = useTheme()

  if (!summary) return null
  const { kpi, asset_table } = summary
  const assets = asset_table.rows

  return (
    <div style={{ padding: '32px 32px 40px', overflow: 'auto' }}>
      <div style={{ marginBottom: 22 }}>
        <div style={{ fontSize: 11, fontWeight: 600, letterSpacing: '.1em', textTransform: 'uppercase', color: theme.palette.text.secondary }}>Opportunities</div>
        <h2 style={{ margin: '4px 0 0', fontSize: 28, fontWeight: 700, letterSpacing: '-0.025em', color: theme.palette.text.primary }}>What should I do next?</h2>
      </div>

      {/* Priority actions */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: 18, marginBottom: 18 }}>
        <Rebalance assets={assets} portfolioValue={kpi.value} />
        <TaxLoss assets={assets} />
        <CashDeploy cash={kpi.cash} />
      </div>

      {/* Mid row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 18, marginBottom: 18 }}>
        <DividendCalendar assets={assets} />
        <Earnings assets={assets} />
      </div>

      {/* Discovery */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: 18 }}>
        <ConcentrationWarn assets={assets} portfolioValue={kpi.value} />
        <SectorGaps assets={assets} />
        <SimilarPicks />
      </div>
    </div>
  )
}
