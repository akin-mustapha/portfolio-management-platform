# Typography

Source of truth: `src/dashboard/assets/base.css`, `src/dashboard/app.py`.

---

## Font Family

Canonical fallback stack (defined in `base.css`, applied to `body, *`):

```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
```

Some component-level CSS (e.g. `sidebar.css`, `components.css`) uses the shorthand `Inter, system-ui, sans-serif`. Both are acceptable — the global `base.css` declaration takes precedence via inheritance for most elements.

Loaded from Google Fonts in `app.py`:
```
https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap
```

Weights loaded: **400, 500, 600, 700**.

---

## Font Size Scale

| Usage | Size | px equiv |
|---|---|---|
| KPI value (large) | `1.125rem` | ~18px |
| Section header / label | `0.8rem` | ~12.8px |
| Sidebar nav item | `0.8125rem` | 13px |
| Asset header name (muted) | `0.72rem` | ~11.5px |
| Badge / chip text | `11px` | 11px |
| Small label (uppercase) | `11px` | 11px |
| Rebalance panel text | `12px` | 12px |
| Rebalance slider label | `11px` | 11px |
| AG Grid body | `12.5px` or `13px` | — |
| AG Grid header | `11px` | 11px |
| Button text | `12px` | 12px |
| Date picker input | `12px` | 12px |
| Theme toggle icon | `1.1rem` | ~17.6px |

---

## Font Weights

| Weight | Usage |
|---|---|
| 400 | Body text, ghost button, asset header name |
| 500 | Sidebar nav, outlined button, filter labels |
| 600 | Section headers, section title, apply button, badge text, active nav |
| 700 | Active timeframe button, pnl positive/negative in grid |

---

## Text Transform & Letter Spacing

Used for uppercase label style (filter labels, panel titles, AG Grid headers):

```css
text-transform: uppercase;
letter-spacing: 0.05em;  /* general labels */
letter-spacing: 0.04em;  /* badge/chip text */
letter-spacing: 0.5px;   /* date picker label (.tv-date-label) */
```

Applied to: `.rebalance-panel-title`, `.tv-date-label`, `.profile-tag-chip`, `.asset-ticker-tag`, AG Grid column headers.

---

## Icon Library

Font Awesome (solid) is loaded via `dbc.icons.FONT_AWESOME` in `app.py`.
Used for: theme toggle (`fa-moon` / `fa-sun`), privacy toggle (`fa-eye` / `fa-eye-slash`), nav icons.
