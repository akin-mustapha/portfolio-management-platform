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

# Dashboard Structure

```
src/dashboard/
  app.py                          — Dash app init, registers pages
  layouts/                        — Top-level shell (sidebar, horizontal bar)
  pages/portfolio/
    portfolio_page.py             — Page layout definition
    callbacks.py                  — All data callbacks (7 callbacks)
    theme_callbacks.py            — Theme + privacy toggle callbacks
    components/
      kpis.py                     — KPI row builder
      tables.py                   — Asset AG Grid table
      charts.py                   — Winners/losers bar charts
      asset_charts.py             — Per-asset workspace charts
      filter_bar.py               — Timeframe selector + advanced filters
      workspace_tabs.py           — Tab content builders (portfolio/valuation/risk/opportunities)
  controllers/                    — Fetch + assemble view models
  presenters/                     — Shape data for display
  infrastructure/repositories/    — SQL queries
```

# UI Reference

See `./references/ui-lingo.md` for:
- Layout vocabulary (what "side by side" means in code)
- Component names and their Dash equivalents
- All chart IDs and container IDs
- Theme colours for dark/light mode
