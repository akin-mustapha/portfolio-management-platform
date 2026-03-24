# Design Tokens

Source of truth: `src/dashboard/assets/theme.css` and `src/dashboard/assets/base.css`.

**Rule: always use CSS variables. Never hardcode a color in CSS except in `_helpers.py` and `theme.py`.**

---

## Color Tokens — Light / Dark

All variables are defined in `theme.css`. Light mode is `:root`, dark mode is `html[data-theme="dark"]`.

| Token | Light | Dark |
|---|---|---|
| `--bg-app` | `#ffffff` | `#1e222d` |
| `--bg-sidebar` | `#f8f9fa` | `#161b27` |
| `--bg-kpi-card` | `#f8f9fa` | `#252d3d` |
| `--bg-panel` | `#f8f9fa` | `#1a1f2e` |
| `--bg-filter-bar` | `#fafbfd` | `#1a1f2e` |
| `--bg-strip-hover` | `#f0f3fa` | `#252d3d` |
| `--bg-strip-active` | `#eef2ff` | `#1c2a4a` |
| `--bg-picker` | `#ffffff` | `#252d3d` |
| `--bg-row-even` | `#ffffff` | `#1e222d` |
| `--bg-row-odd` | `#f8f9fb` | `#222839` |
| `--bg-row-hover` | `#eaf2ff` | `#1c2a4a` |
| `--bg-row-selected` | `#dbeafe` | `#1a3158` |
| `--border-split` | `#dee2e6` | `#2a3042` |
| `--border-main` | `#e9ecef` | `#2a3042` |
| `--border-grid` | `#e2e4e9` | `#2a3042` |
| `--border-row` | `#e8eaed` | `#2a3042` |
| `--border-tv` | `#e0e3eb` | `#2a3042` |
| `--text-primary` | `#131722` | `#d1d4dc` |
| `--text-secondary` | `#6b7280` | `#9598a1` |
| `--text-muted` | `#adb5bd` | `#6b7280` |
| `--text-nav` | `#495057` | `#9598a1` |
| `--scrollbar-thumb` | `#c8cbd4` | `#3d4460` |
| `--sidebar-shadow` | `#e9ecef` | `#0d1117` |
| `--chart-bg` | `#ffffff` | `#1e222d` |
| `--chart-font` | `#555555` | `#9598a1` |

---

## Asset Identity Colors

Per-asset stripe, header accent, and chart line colors. Defined in `base.css`.

Unlike `--bg-*` and `--text-*` tokens, these are **not switched by `html[data-theme="dark"]`**. Both the light and dark variants are defined as separate variable names under `:root`, and components reference the dark name explicitly inside their own `html[data-theme="dark"]` selectors.

| Light variable | Value | Dark variable | Value |
|---|---|---|---|
| `--asset-1-color` | `#0d6efd` (blue) | `--asset-1-color-dark` | `#639aff` |
| `--asset-2-color` | `#26a671` (green) | `--asset-2-color-dark` | `#4cbb9f` |
| `--asset-3-color` | `#ef5350` (red) | `--asset-3-color-dark` | `#f47c7c` |

Usage pattern in CSS:
```css
.tv-section-container--asset-1 { border-left: 3px solid var(--asset-1-color); }
html[data-theme="dark"] .tv-section-container--asset-1 { border-left-color: var(--asset-1-color-dark); }
```

Applied via modifier classes: `tv-section-container--asset-1`, `tv-section-header--asset-1`, etc.
Python maps in `_helpers.py` hold the hex values directly for passing to Plotly.

---

## Workspace Spacing Tokens

Defined in `base.css`. Change here to adjust spacing globally.

| Token | Value | Used for |
|---|---|---|
| `--ws-section-pad-v` | `12px` | vertical padding inside `.tv-section-container` |
| `--ws-section-pad-h` | `12px` | horizontal padding inside `.tv-section-container` |
| `--ws-section-gap` | `12px` | `margin-bottom` between section containers |
| `--ws-header-pad-v` | `10px` | vertical padding in `.tv-section-header` |
| `--ws-header-pad-h` | `6px` | horizontal padding in `.tv-section-header` |
| `--ws-divider-v` | `12px` | vertical margin above/below `.tv-divider` |
| `--ws-chart-gap` | `8px` | gap between charts in `.workspace-chart-grid` |
| `--ws-chart-pad-h` | `12px` | horizontal padding in `.workspace-chart-grid` |
| `--ws-row-pad-v` | `5px` | movers/ranked row vertical padding |
| `--ws-row-pad-h` | `8px` | movers/ranked row horizontal padding |
| `--ws-row-gap` | `2px` | `margin-bottom` between movers rows |
| `--ws-tab-pad` | `8px` | padding inside `#tab-*-content` panes |

---

## Hardcoded Brand Colors (not tokens)

These appear in CSS and Python but are not CSS variables — they are the project's fixed brand palette.

| Color | Hex | Usage |
|---|---|---|
| Primary blue | `#0d6efd` | Bootstrap primary, focus rings, active nav |
| Action blue | `#2962ff` | Apply button bg, active timeframe underline |
| Indigo (slider) | `#6366f1` | Rebalance slider track |
| Hover blue light | `#eef2ff` | Button hover bg |
| Hover border | `#a5b4fc` | Button hover border |
| Focus shadow | `rgba(13, 110, 253, 0.25)` | Form focus ring |
