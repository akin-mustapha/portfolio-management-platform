# Frontend React Migration Plan

Migrate the existing Dash dashboard to a React + Material UI application. Both UIs run concurrently until the React frontend reaches feature parity and is validated in daily use.

---

## Goals

- Replace the Dash (Python) dashboard with a React + TypeScript SPA
- Use Material UI v5 as the component library
- Keep Plotly for all charts (no chart library rewrite)
- Build a proper REST API layer (FastAPI) that React consumes
- Run both UIs simultaneously during the transition — no forced cutover
- Root folder: `frontend/`

---

## Stack

| Concern | Choice | Reason |
|---|---|---|
| Build tool | Vite | Fast, minimal config |
| UI framework | React 18 + TypeScript | Type safety, ecosystem |
| Component library | Material UI v5 | Built-in theming, dark mode, DataGrid |
| Charts | recharts | React-native, declarative, lighter weight; all required chart types supported |
| Data fetching | TanStack Query (React Query) | Caching, background refresh, loading states |
| State management | Zustand | Lightweight — selected assets, theme, filters, privacy |
| Routing | React Router v6 | Single route today, extensible |
| Table | MUI DataGrid | Replaces AG Grid |
| Resizable panels | react-resizable-panels | Replaces custom drag-drop JS |
| API | FastAPI | Already a project dependency; reuse existing controllers |

---

## Coexistence Architecture

```
Port 8050  →  Dash (existing, unchanged, kept alive)
Port 8001  →  FastAPI (new REST API + serves React build in production)
Port 5173  →  Vite dev server (development only)
```

Both UIs share the same PostgreSQL database. No data duplication. FastAPI is a new process — does not touch or replace the Dash server.

In production, FastAPI serves the React build as static files:

```python
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
```

---

## Directory Structure

```
frontend/                          # React application root
├── index.html
├── vite.config.ts
├── tsconfig.json
├── package.json
├── public/
│   └── favicon.ico
└── src/
    ├── main.tsx                   # App entry point
    ├── App.tsx                    # Router + ThemeProvider
    ├── theme/
    │   ├── theme.ts               # MUI createTheme (light + dark)
    │   └── tokens.ts              # Design tokens (maps from CSS vars)
    ├── api/
    │   ├── client.ts              # Axios instance + base URL config
    │   ├── portfolio.ts           # Portfolio API calls
    │   ├── assets.ts              # Asset API calls
    │   ├── tags.ts                # Tag API calls
    │   ├── rebalance.ts           # Rebalancing API calls
    │   └── credentials.ts        # Credentials API calls
    ├── store/
    │   └── useAppStore.ts         # Zustand store (theme, privacy, filters, selection)
    ├── hooks/
    │   ├── usePortfolio.ts        # React Query hook — portfolio summary
    │   ├── useAssets.ts           # React Query hook — asset table rows
    │   ├── useAssetHistory.ts     # React Query hook — per-asset time series
    │   └── useRebalance.ts        # React Query hook — rebalance configs + plan
    ├── components/
    │   ├── atoms/
    │   │   ├── KpiCard.tsx        # Single KPI metric card
    │   │   ├── PnlBadge.tsx       # Green/red P&L chip
    │   │   └── PrivacyValue.tsx   # Masked value when privacy mode on
    │   ├── molecules/
    │   │   ├── KpiRow.tsx         # 7-card portfolio summary row
    │   │   ├── FilterBar.tsx      # Timeframe + tag + date filters
    │   │   └── StatusBar.tsx      # Selected asset count / status
    │   ├── organisms/
    │   │   ├── Navbar.tsx         # Top navigation bar
    │   │   ├── AssetTable.tsx     # MUI DataGrid (25 columns, conditional styling)
    │   │   ├── WorkspaceSplit.tsx # Resizable left/right panel container
    │   │   ├── WorkspaceTabs.tsx  # 4-tab container
    │   │   ├── RebalanceDrawer.tsx# Slide-in rebalancing panel
    │   │   ├── SettingsModal.tsx  # API credentials dialog
    │   │   └── EditTagsModal.tsx  # Asset tag editing dialog
    │   └── charts/
    │       ├── PortfolioValueChart.tsx
    │       ├── PortfolioPnlChart.tsx
    │       ├── PositionWeightChart.tsx
    │       ├── WinnersChart.tsx
    │       ├── LosersChart.tsx
    │       ├── DailyMoversTable.tsx
    │       ├── DrawdownChart.tsx
    │       ├── ProfitabilityChart.tsx
    │       ├── VarByPositionChart.tsx
    │       ├── UnprofitablePnlChart.tsx
    │       ├── OpportunitiesChart.tsx
    │       ├── AssetValueChart.tsx
    │       ├── AssetPnlChart.tsx
    │       ├── AssetReturnChart.tsx
    │       └── SparklineChart.tsx
    └── pages/
        └── portfolio/
            ├── PortfolioPage.tsx
            └── tabs/
                ├── PortfolioTab.tsx
                ├── RiskTab.tsx
                ├── OpportunitiesTab.tsx
                └── AssetProfileTab.tsx
```

```
src/api/                           # FastAPI application (new)
├── main.py                        # FastAPI app + mounts React build
├── routers/
│   ├── portfolio.py               # GET /api/portfolio/summary, /history
│   ├── assets.py                  # GET /api/assets, /api/assets/{ticker}/history
│   ├── tags.py                    # GET /api/tags, PUT /api/assets/{ticker}/tags
│   ├── rebalance.py               # GET/POST /api/rebalance/configs, POST /api/rebalance/plan
│   └── credentials.py            # GET/POST /api/credentials (ported from Flask Blueprint)
└── dependencies.py                # DB session, shared deps
```

---

## API Endpoints to Build

All endpoints reuse existing controllers, repositories, and presenters. No new business logic.

| Method | Path | Source (existing) | Used by |
|---|---|---|---|
| `GET` | `/api/portfolio/summary` | `PortfolioController.get_data()` + `PortfolioPresenter` | KPI row, all portfolio charts |
| `GET` | `/api/portfolio/history` | `get_unrealized_profit()`, `get_portfolio_price_history()` | Timeframe filter re-fetch |
| `GET` | `/api/assets` | `get_most_recent_asset_data()` | Asset table |
| `GET` | `/api/assets/{ticker}/history` | `get_asset_history()` | Asset Profile tab charts |
| `GET` | `/api/assets/{ticker}/profile` | `AssetProfileController` | Asset Profile tab metadata |
| `GET` | `/api/tags` | `get_asset_tags()` | Tag filter dropdown |
| `PUT` | `/api/assets/{ticker}/tags` | `update_asset_tags()` | Edit Tags modal |
| `GET` | `/api/rebalance/configs` | `RebalancingService.load_configs()` | Rebalance drawer |
| `POST` | `/api/rebalance/configs` | `RebalancingService.save_config()` | Save weight sliders |
| `POST` | `/api/rebalance/plan` | `RebalancingService.generate_plan()` | Generate plan button |
| `GET` | `/api/credentials` | `CredentialsRepository.load()` | Settings modal |
| `POST` | `/api/credentials` | `CredentialsRepository.save()` | Settings modal |

Query parameters:
- `/api/portfolio/history?from=YYYY-MM-DD&to=YYYY-MM-DD`
- `/api/assets/{ticker}/history?from=YYYY-MM-DD&to=YYYY-MM-DD`
- `/api/assets?tags=tag1,tag2` (tag filter)

---

## Theme Mapping

MUI theme tokens mapped from existing CSS custom properties:

```typescript
// frontend/src/theme/theme.ts
const lightTokens = {
  primary:    '#0d6efd',
  positive:   '#26a671',
  negative:   '#ef5350',
  bgApp:      '#ffffff',
  bgSidebar:  '#f8f9fa',
  textPrimary:'#131722',
}

const darkTokens = {
  primary:    '#639aff',
  positive:   '#4cbb9f',
  negative:   '#f47c7c',
  bgApp:      '#1e222d',
  bgSidebar:  '#161b27',
  textPrimary:'#d1d4dc',
}
```

Per-asset color tokens (3 assets, light + dark variant each) carry over unchanged into the MUI theme's custom palette extensions.

Dark mode preference persisted to `localStorage` via Zustand middleware — same behaviour as current `theme-store`.

---

## Phases

### Phase 0 — FastAPI Layer (Week 1–2)

**Goal:** All data accessible over HTTP. React can be built against real data from day one.

Tasks:
- Create `src/api/main.py` — FastAPI app
- Port `credentials_routes.py` Flask blueprint → FastAPI router
- Implement `GET /api/portfolio/summary` — wire `PortfolioController` + `PortfolioPresenter`
- Implement `GET /api/assets` and `GET /api/portfolio/history`
- Implement asset history + profile endpoints
- Implement tags read/write endpoints
- Implement rebalancing endpoints
- Add CORS middleware (allow Vite dev server origin)
- Verify all endpoints return correct JSON against the running DB

Deliverable: All 12 endpoints returning real data. Dash unchanged.

---

### Phase 1 — Project Scaffold (Week 1, parallel with Phase 0)

**Goal:** React project builds, runs, connects to the API, renders a placeholder page.

Tasks:
- Initialise `frontend/` with Vite (`npm create vite@latest frontend -- --template react-ts`)
- Install dependencies: MUI, recharts, TanStack Query, Zustand, React Router, Axios, react-resizable-panels
- Configure Vite proxy (`/api → http://localhost:8001`)
- Set up MUI ThemeProvider with light/dark tokens
- Set up Zustand store (theme, privacy, timeframe, selectedTickers)
- Set up TanStack QueryClient
- Add React Router with a `/portfolio` route
- Confirm app loads and API proxy works

Deliverable: `frontend/` boots, `GET /api/portfolio/summary` succeeds in the browser.

---

### Phase 2 — Core Layout + Asset Table (Week 2–3)

**Goal:** The two highest-value UI elements are live with real data.

Tasks:
- `Navbar.tsx` — MUI AppBar, brand, theme toggle, privacy toggle, settings button
- `KpiCard.tsx` + `KpiRow.tsx` — 7 portfolio KPI cards, responsive MUI Grid
- `AssetTable.tsx` — MUI DataGrid
  - Map all 25 columns from `GET /api/assets`
  - Conditional cell coloring (green/red P&L)
  - Column visibility toggle (MUI DataGrid built-in)
  - Row selection → update `selectedTickers` in Zustand
- `FilterBar.tsx` — MUI Select (timeframe), Autocomplete (tag multi-select)
- `StatusBar.tsx` — selected asset count below table
- `WorkspaceSplit.tsx` — react-resizable-panels, persist split ratio to localStorage

Deliverable: Portfolio page renders with live KPI row, filterable asset table, resizable split.

---

### Phase 3 — Charts + Tabs (Week 3–4)

**Goal:** All 4 tabs rendering with real chart data.

Tasks:
- `WorkspaceTabs.tsx` — MUI Tabs, 4 tab panels
- Build all 14 portfolio chart components using Recharts (`LineChart`, `AreaChart`, `BarChart`, `PieChart`, `ComposedChart` as appropriate)
- `PortfolioTab.tsx` — value chart, P&L chart, position weight donut, winners/losers bars, movers
- `RiskTab.tsx` — drawdown, profitability donut, VaR by position, unprofitable P&L
- `OpportunitiesTab.tsx` — potential gains, entry point analysis
- Theme-aware chart colors — pass palette values from MUI theme directly as props (no `useEffect` needed; Recharts rerenders on prop change)
- Collapsible chart sections (MUI `Accordion`)

Deliverable: All portfolio-level charts rendering with live data and dark mode support.

---

### Phase 4 — Asset Selection + Asset Profile Tab (Week 4–5)

**Goal:** Selecting a row in the table populates the Asset Profile tab with per-asset charts and metadata.

Tasks:
- Wire `selectedTickers` Zustand → `useAssetHistory` React Query hooks
- Build 9 asset chart components using Recharts
- `AssetProfileTab.tsx` — asset KPIs, technical charts, tags display
- `EditTagsModal.tsx` — MUI Dialog + Autocomplete multi-select, `PUT /api/assets/{ticker}/tags`
- Asset comparison mode (1–3 tickers selected simultaneously)
- `PrivacyValue.tsx` — mask monetary values when privacy mode active

Deliverable: Asset selection drives Asset Profile tab with real per-asset data.

---

### Phase 5 — Rebalancing + Settings + Parity (Week 5–6)

**Goal:** Full feature parity. Both UIs in daily use. Cutover decision made.

Tasks:
- `RebalanceDrawer.tsx` — MUI Drawer (slide in from bottom), MUI Slider per asset, save + generate
- `SettingsModal.tsx` — MUI Dialog, credential inputs, show/hide password, connection test
- Timeframe filter re-fetch — date window change triggers React Query invalidation
- Advanced filter (custom date range) — MUI DateRangePicker
- Feature parity audit — walk every Dash callback, confirm React equivalent exists
- Fix gaps found in audit
- Run both UIs in daily use for one week
- Cutover: update default entry point to React; keep Dash available but not default

Deliverable: Feature parity confirmed. React is the primary UI.

---

## Effort Summary

| Phase | Scope | Weeks |
|---|---|---|
| 0 | FastAPI REST API | 1.5 |
| 1 | React scaffold + project setup | 0.5 |
| 2 | Navbar, KPI row, Asset Table, FilterBar, Split | 1.5 |
| 3 | All charts, 4 tabs | 1.5 |
| 4 | Asset selection, Asset Profile, tag editing | 1.0 |
| 5 | Rebalancing, Settings, parity audit, cutover | 1.0 |
| **Total** | | **~7 weeks** |

---

## What Does Not Change

- PostgreSQL database and all three schema layers (`raw`, `staging`, `analytics`)
- All pipelines and Prefect orchestration
- Existing Dash dashboard (kept alive throughout)
- Existing Flask credential endpoints (ported to FastAPI, originals remain until cutover)
- Chart data shapes — view models from existing presenters become API response bodies

---

## Risks

| Risk | Mitigation |
|---|---|
| API response shape mismatch from presenter output | Write one endpoint, validate JSON in browser before building the component against it |
| MUI DataGrid missing AG Grid features (e.g. conditional row styling) | Evaluate early in Phase 2 — fall back to `react-table` + custom styling if needed |
| Recharts dual-axis charts require `ComposedChart` with careful axis config | Prototype `VarByPositionChart` first in Phase 3 — it's the most complex axis layout — before building remaining charts |
| Split panel behaviour differs from current drag-drop JS | Test `react-resizable-panels` in Phase 2 scaffold before committing |
