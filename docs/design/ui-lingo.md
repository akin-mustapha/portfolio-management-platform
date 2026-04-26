# UI Lingo Guide — Dash Dashboard

A reference for describing UI changes precisely so Claude gets it right first time.

---

## The Grid System (Bootstrap 12-column)

The dashboard uses **Dash Bootstrap Components (dbc)**. The layout system works like a spreadsheet: every row has 12 columns, and you divide them up between your components.

```
|-------- 12 columns total --------|
| col=6 (half)  | col=6 (half)     |   ← side by side, equal
| col=4 | col=4 | col=4            |   ← three equal thirds
| col=3  | col=9                   |   ← sidebar + main content
| col=12 (full width)              |   ← one thing spanning the whole row
```

**The building blocks:**
- `dbc.Row` — a horizontal container. Everything inside sits side by side.
- `dbc.Col(width=N)` — a column of width N (1–12). Wraps each item inside a Row.
- `html.Div` — a plain box. Stacks vertically by default (no Row needed).

---

## Layout Vocabulary: What to Say

| Instead of saying... | Say this |
|---|---|
| "side by side" | `dbc.Row` with two `dbc.Col(width=6)` |
| "three across" | `dbc.Row` with three `dbc.Col(width=4)` |
| "full width" | `dbc.Col(width=12)` or no Col wrapper |
| "sidebar on the left" | `dbc.Col(width=3)` left + `dbc.Col(width=9)` right |
| "stacked / underneath" | separate `html.Div` blocks (no Row) |
| "centered" | `dbc.Col(width=6, offset=3)` or `className="text-center"` |
| "make it smaller / tighter" | reduce `width=` value or add `style={"maxWidth": "Xpx"}` |
| "responsive — stacks on mobile" | `dbc.Col(md=6, xs=12)` (md= for desktop, xs= for mobile) |

---

## Component Names

These are the actual Dash components used in this project:

| What it looks like | Component name |
|---|---|
| A chart (bar, line, donut) | `dcc.Graph` — has a `figure` prop |
| A card / white box | `dbc.Card` + `dbc.CardBody` |
| A tab panel | `dbc.Tabs` + `dbc.Tab` |
| A loading spinner | `dcc.Loading` (wraps another component) |
| A dropdown | `dcc.Dropdown` or `dbc.Select` |
| A toggle / switch | `dbc.Switch` |
| A collapsible section | `dbc.Collapse` — open/close via `is_open` prop |
| A badge / label chip | `dbc.Badge` |
| A tooltip on hover | `dbc.Tooltip` pointing at a component id |
| Invisible data store | `dcc.Store` — holds data between callbacks |

---

## Chart Vocabulary (Plotly)

Every `dcc.Graph` displays a Plotly `figure`. The figure has two parts:

- **`data`** — the actual data series, called **traces** (e.g. one bar series, one line)
- **`layout`** — the styling: background colour, axis labels, title, font

**Chart types used in this project:**
| What you see | Plotly name |
|---|---|
| Bar chart | `go.Bar` / `px.bar` |
| Line chart | `go.Scatter` / `px.line` |
| Donut / ring chart | `go.Pie` with `hole=0.5` |
| Heatmap / treemap | `go.Treemap` |
| Drawdown chart | `go.Scatter` with fill |

**Chart properties to reference:**
- `paper_bgcolor` — background behind the whole chart
- `plot_bgcolor` — background inside the axes
- `font.color` — text colour (axis labels, title)
- `margin` — space around the chart (`dict(l=0, r=0, t=30, b=0)`)
- `showlegend` — whether the legend appears

---

## Callbacks — What Connects UI to Python

A **callback** is a Python function that runs when something in the UI changes.

- **`Output`** — what the callback writes to (a component + its prop)
- **`Input`** — what triggers the callback (user clicks, dropdown changes, page load)
- **`State`** — extra data the callback reads but doesn't react to

**Key rule:** Two callbacks cannot write to the same `Output(id, prop)` unless one uses `allow_duplicate=True`. This is the duplicate callback error.

---

## Component IDs in This Project

These are the live IDs in the dashboard. Use these exact strings when describing changes:

**Stores (invisible data)**
- `theme-store` — `"light"` or `"dark"`
- `privacy-store` — `True` / `False`
- `portfolio_page_asset_store` — cached page data
- `workspace-selected-asset` — currently selected ticker
- `workspace-timeframe` — selected timeframe string

**Charts**
- `value_chart`, `pnl_chart` — portfolio value and P&L line charts (Valuation tab)
- `position_weight_donut_chart`, `portfolio_fx_attribution_chart` — allocation + FX attribution donuts (Valuation tab)
- `portfolio_drawdown_chart`, `profitability_donut_chart` — drawdown + P&L profitability (Risk tab)
- `losers_pnl_chart`, `var_by_position_chart` — unprofitable positions + VaR (Risk tab)
- `portfolio_performance_map`, `winners_pnl_chart` — scatter + winners P&L (Opportunities tab)

**Ranked panels (not charts — HTML rows)**
- `winners-table`, `losers-table` — top winners/losers ranked rows (Valuation tab)
- `daily-movers-table` — today's movers list (Valuation tab)

**Containers (filled by callbacks)**
- `portfolio_kpi_container` — KPI row
- `portfolio_page_asset_table_container` — asset table
- `tab-portfolio-content` — Valuation tab panel
- `tab-risk-content` — Risk tab panel
- `tab-opportunities-content` — Opportunities tab panel

**Layout / workspace**
- `workspace-split` — the drag-to-resize split panel
- `workspace-left`, `workspace-right` — the two panels
- `workspace-adv-filter-collapse` — advanced filter collapse panel

---

## Theme System

Dark/light mode is driven by `theme-store`. Charts patch their `paper_bgcolor`, `plot_bgcolor`, and `font.color` via the `update_chart_theme` callback in `theme_callbacks.py`.

When adding a new chart, it must be added to that callback's `Output` list — otherwise it won't respond to theme changes.

Dark mode colours:
- Background: `#1e222d`
- Font: `#9598a1`
- Range selector bg: `#252d3d`

Light mode colours:
- Background: `white`
- Font: `#555555`
