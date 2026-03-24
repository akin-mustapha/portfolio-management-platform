---
name: ui
description: Use this skill when working on any visual aspect of the dashboard — adding or modifying components, choosing colors, sizing text, adjusting spacing, or ensuring dark mode compatibility. Covers the complete visual language: tokens, typography, theming, component patterns, and sentiment colors.
---

# Why

The visual language is spread across 8 CSS files and 3 Python files. This skill consolidates all of it so UI work stays consistent without reading every source file. Use it any time you're about to write or modify CSS, add a component, choose a color, or touch theme behavior.

# Rules

1. **Never hardcode colors in CSS.** Use `var(--token-name)`. Exceptions: the brand palette table in `tokens.md` (those are fixed values used as token inputs, not inline styles).
2. **Never hardcode colors in Python** except inside `_helpers.py` (asset color maps) and `theme.py` (chart bg/font patch). Anywhere else, derive the value from those maps.
3. **Any new `dcc.Graph` must be wired into `update_chart_theme`.** Adding a chart without wiring it breaks dark mode. See `theming.md`.
4. **Always check both light and dark mode** when adding a new component. If a component lacks a `html[data-theme="dark"]` override and uses hardcoded colors, it will break in dark mode.
5. **Use existing component classes before writing new CSS.** Check these before inventing new styles:
   - Containers/headers: `.tv-section-container`, `.tv-section-header`, `.tv-divider`, `.tv-vert-divider`
   - Buttons: `.tv-apply-btn`, `.tv-adv-btn`, `.tv-ghost-btn`, `.top-util-btn`
   - Tags/badges: `.profile-tag-chip`, `.asset-ticker-tag`, `.kpi-badge`, `.kpi-badge--action`
   - Filter bar: `.workspace-filter-bar`, `.tv-timeframe-strip`, `.tv-collapse-body`, `.tv-single-picker`
   - Layout: `.rebalance-drawer`, `.sidebar-nav-item`
   - Modals: `.ws-modal-card` (Edit Tags), `.settings-modal` (Settings)
6. **Spacing comes from tokens.** Use `var(--ws-*)` variables for section/chart/row spacing — don't hardcode padding and gap values that duplicate what's in `base.css`.

# Visual Language Summary

- **Font:** Inter (400/500/600/700), loaded from Google Fonts
- **Base theme:** Bootstrap COSMO + CSS variable override system
- **Theme toggle:** `data-theme` attribute on `<html>`, toggled via clientside callback
- **Bootstrap blue** `#0d6efd` — nav active state, focus rings, AG Grid header text/bg, form focus shadows
- **Action blue** `#2962ff` — apply button background, active timeframe underline. These two blues are not interchangeable.
- **Positive:** `#26a671` / Negative: `#ef5350`
- **Border radius:** 8px (containers), 4px (controls/buttons), 12px (pills)
- **Section spacing:** all controlled by `--ws-*` tokens in `base.css`

# CSS Class Naming Convention

The codebase uses a two-tier system. Follow this when writing any new class names.

## Tier 1 — Design system primitives (`tv-` prefix)

Reusable components that appear across multiple features. Use `tv-` as the namespace with BEM-style modifiers:

```
tv-{block}                   # base component
tv-{block}--{modifier}       # variant (e.g. tv-section-header--asset-1)
tv-{block}__{element}        # sub-element (e.g. tv-section-header__chevron)
```

Examples: `.tv-section-container`, `.tv-section-container--asset-1`, `.tv-apply-btn`, `.tv-divider`, `.tv-vert-divider`

## Tier 2 — Feature namespaces

Feature-specific components use the feature name as a flat prefix:

```
{feature}-{block}            # block    (e.g. rebalance-drawer)
{feature}-{block}-{element}  # element  (e.g. rebalance-drawer-inner)
{feature}-{block}--{modifier} # modifier (e.g. rebalance-action--reduce)
```

Established feature namespaces:

| Prefix | Feature | Source file |
|---|---|---|
| `rebalance-` | Rebalance panel and drawer | `sidebar.css` |
| `sidebar-` | Sidebar nav | `sidebar.css` |
| `kpi-` | KPI cards and badges | `ag-grid-finance.css` |
| `workspace-` | Page layout containers | `layout.css` |
| `ws-modal-` | Edit Tags modal | `components.css` |
| `settings-` | Settings modal | `components.css` |
| `profile-` | Asset profile section | `components.css` |
| `movers-` | Daily movers table | `components.css` |

## Rules

1. **Never invent a new prefix.** New feature components belong under the closest existing feature namespace or `tv-` if reusable across features.
2. **`ws-modal-` means Edit Tags modal only.** Do not use `ws-` for other modals — use the feature name instead (e.g. `confirm-modal-*`).
3. **Modifier classes use `--` (double dash).** Sub-elements within a feature block use a single `-` hyphen.
4. **No camelCase in class names.** All lowercase with hyphens only.

---

# References

- [tokens.md](./references/tokens.md) — all CSS custom properties (color, spacing, asset identity), light and dark values side by side
- [typography.md](./references/typography.md) — font family, size scale, weights, text-transform patterns
- [theming.md](./references/theming.md) — how light/dark switching works end-to-end, Python chart color constants, privacy mode
- [sentiment-colors.md](./references/sentiment-colors.md) — gain/loss colors, rebalance badges, slider, primary action color
- [components.md](./references/components.md) — border-radius reference, button specs, badge specs, section container, KPI badges, filter bar, modals, AG Grid, nav
