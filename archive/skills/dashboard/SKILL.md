---
name: dashboard
description: Use this skill when working on the Dash dashboard — adding components, fixing layouts, modifying callbacks, or updating charts.
---

# Why

This provides the context needed to work on the dashboard correctly and avoid the most common failure modes: duplicate callbacks, broken theme support, and layout misinterpretations.

# Rules (enforce these before touching any code)

1. **Search for duplicate outputs first.** Before adding any `Output('id', 'prop')`, grep for it across the entire `src/dashboard/` directory.
2. **Any new chart must be added to `theme_callbacks.py`.** Both the portfolio callback (`update_chart_theme`) and the workspace callback (`update_workspace_chart_theme`) patch chart colours on theme change. New charts must be wired in.
3. **Never remove `theme-store` or `privacy-store` reads.** These stores are used across many callbacks — they are not dead code even if a specific function doesn't appear to use the value.
4. **Confirm layout direction before implementing.** If the user says "side by side", confirm it means `dbc.Row` + two `dbc.Col(width=6)`. Do not assume.
5. **`dcc.Loading` can break table rendering.** Use with caution around AG Grid or complex table components — test that the component still renders after wrapping.
6. **Callbacks must not instantiate presenters directly.** The pattern is: callback → controller → presenter. Presenters are called only from within their paired controller. If a callback needs a re-sort or re-filter on cached data, add a method to the relevant controller — do not reach into the presenter from a callback.
7. **Tab content functions must not carry the placeholder ID.** `_loading_placeholder(tab_id, ...)` creates the stable DOM anchor with that ID. The full content function (called with real data) must return a plain `html.Div` without that ID — otherwise every callback trigger nests a duplicate ID inside the placeholder.

# Dashboard Structure

```
src/dashboard/
  app.py                          — Dash app init, registers pages
  assets/                         — CSS (split by concern)
    theme.css                     — light/dark colour variables
    base.css                      — typography + spacing tokens
    layout.css                    — navbar, split panels, filter bar
    components.css                — buttons, badges, tabs, modals (11 sections)
    charts.css                    — chart grids + chart headers
    ag-grid-finance.css           — AG Grid table styling
  components/                     — shared UI atoms across all pages
    atoms/
      buttons.py                  — privacy_toggle_btn and shared buttons
  layouts/                        — top-level shell (navbar, page router)
  pages/portfolio/
    portfolio_page.py             — page layout definition
    callbacks.py                  — orchestrator: imports all callback sub-modules
    callbacks_data.py             — page load + daily movers
    callbacks_filters.py          — timeframe selector + tag filter
    callbacks_selection.py        — row selection, compare mode, asset profile
    callbacks_tags.py             — edit tags modal (open / save / close)
    callbacks_ui.py               — collapse toggles (no data dependency)
    _callback_helpers.py          — shared: date window, fetch, build_compare_rows
    theme_callbacks.py            — theme + privacy toggle callbacks
    settings_callbacks.py         — settings modal callbacks
    tabs/                         — one file per tab (layout only, no callbacks)
      tab_portfolio.py            — Valuation tab
      tab_risk.py                 — Risk tab
      tab_opportunities.py        — Opportunities tab
      tab_asset_profile.py        — Asset Profile tab
      _helpers.py                 — _chart_section, _loading_placeholder, _GRAPH_CONFIG
    charts/                       — front door for chart imports
      portfolio_charts.py         — all portfolio chart classes (18 classes/helpers)
      asset_charts.py             — asset comparison chart classes (6 classes)
    components/
      kpis.py                     — KPI row builder
      tables.py                   — Asset AG Grid table
      charts.py                   — portfolio chart implementations (edit chart logic here)
      asset_charts.py             — asset chart implementations (edit chart logic here)
      filter_bar.py               — timeframe selector + advanced filters
      workspace_tabs.py           — tab assembler (calls tabs/ for content)
  controllers/                    — fetch + assemble view models
  presenters/                     — shape data for display
  infrastructure/repositories/    — SQL queries
```

# UI Reference

See `docs/02-architecture/design/ui-design.md`

