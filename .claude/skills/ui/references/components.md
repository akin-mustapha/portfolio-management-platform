# Component Patterns

Source files:

- `src/dashboard/assets/components.css` — section containers, buttons, badges, filter bar, modals, KPI cards
- `src/dashboard/assets/sidebar.css` — sidebar nav, rebalance drawer
- `src/dashboard/assets/layout.css` — top navbar, workspace layout, filter bar container, `.top-util-btn`, `.tv-vert-divider`
- `src/dashboard/assets/ag-grid-finance.css` — AG Grid styles, `.kpi-badge` family, `.tag-badge`, `.tag-row`

---

## Border Radius Reference

| Context | Radius |
|---|---|
| Section containers, rebalance drawer | `8px` |
| Buttons (apply, outlined, ghost) | `4px` |
| Filter collapse body | `0 0 6px 6px` |
| Sidebar nav item | `0 6px 6px 0` |
| Dropdown (rebalance) | `4px` |
| Badge/chip (pill) | `12px` |
| Rebalance action badge | `3px` |
| AG Grid | `6px` |

---

## Section Container

Class: `.tv-section-container`

```css
border: 1px solid var(--border-tv);
border-radius: 8px;
margin-bottom: var(--ws-section-gap);   /* 12px */
padding: 0 var(--ws-section-pad-h) var(--ws-section-pad-v);  /* 0 12px 12px */
```

With asset identity stripe: add modifier class `tv-section-container--asset-1/2/3`.
The stripe is a `3px solid` left border using the asset color variable.

---

## Section Header

Class: `.tv-section-header`

```css
font-size: 0.8rem;
font-weight: 600;
color: var(--text-secondary);
padding: var(--ws-header-pad-v) var(--ws-header-pad-h);  /* 10px 6px */
```

Variant `--section` (collapsible group): color `#0d6efd` (light) / `#639aff` (dark).
Variant `--asset-1/2/3`: uses the matching asset color variable.

---

## Buttons

### `.tv-apply-btn` — Primary solid (Apply, Submit)
```
bg: #2962ff  |  border: #2962ff  |  text: #fff
font: 12px, weight 600, Inter
padding: 4px 16px  |  radius: 4px
hover: bg #eef2ff, border #a5b4fc, text #2962ff
```

### `.tv-adv-btn` — Outlined (Advanced filters, secondary actions)
```
bg: transparent  |  border: var(--border-tv)  |  text: var(--text-secondary)
font: 12px, weight 500, Inter
padding: 4px 12px  |  radius: 4px
hover: bg #eef2ff, border #a5b4fc, text #2962ff
```

### `.tv-ghost-btn` — Ghost (Add Tag, Create Tag, low-emphasis actions)
```
bg: transparent  |  border: none  |  text: var(--text-secondary)
font: 12px, weight 400, Inter
padding: 4px 8px  |  radius: 4px
hover: text var(--text-primary), bg var(--bg-strip-hover)
```

All buttons share: `transition 0.12s ease`, `line-height: 1.6`, `cursor: pointer`.

---

## Badges & Tags

### `.profile-tag-chip` — Asset taxonomy tags (teal)
```
bg: rgba(38, 166, 154, 0.08)  |  border: rgba(38, 166, 154, 0.25)
text: #26a69a  |  radius: 12px
font: 11px, weight 600, letter-spacing 0.04em
padding: 2px 10px
dark: text #4db6ac, slightly stronger bg/border
```

### `.asset-ticker-tag` — Ticker labels (blue)
```
bg: rgba(13, 110, 253, 0.08)  |  border: rgba(13, 110, 253, 0.2)
text: #0d6efd  |  radius: 12px
font: 11px, weight 600, letter-spacing 0.04em
padding: 2px 10px
dark: text #639aff, bg rgba(99, 154, 255, 0.12)
```

---

## Divider

Class: `.tv-divider`

```css
border: none;
border-top: 1px solid var(--border-tv);
margin: var(--ws-divider-v) 0 calc(var(--ws-divider-v) - 4px) 0;  /* ~12px top, 8px bottom */
```

Replaces Bootstrap `<hr>` inside section containers.

---

## Sidebar Nav Item

Class: `.sidebar-nav-item`

```
font: 0.8125rem (13px), weight 500
color: var(--text-nav)
border-left: 3px solid transparent  |  radius: 0 6px 6px 0
hover: bg rgba(13,110,253,0.06), text #0d6efd
active: bg rgba(13,110,253,0.08), text #0d6efd, border-left 3px solid #0d6efd, weight 600
```

---

## Filter Bar

### Timeframe strip (`.tv-timeframe-strip`)
Inline flex radio group. Active item:
```
bg: var(--bg-strip-active)  |  text: #2962ff, weight 700
border-bottom: 2px solid #2962ff
radius: 4px 4px 0 0
```

### Advanced filter collapse body (`.tv-collapse-body`)
```
bg: var(--bg-filter-bar)
border-top: 1px solid var(--border-tv)
radius: 0 0 6px 6px
padding: 7px 14px
```

### Date picker (`.tv-single-picker`)
```
border: 1px solid var(--border-tv)  |  radius: 4px
bg: var(--bg-picker)
input: 12px Inter, text var(--text-primary)
focus: border #2962ff, box-shadow rgba(41,98,255,0.12)
z-index: 9999
```

---

## Rebalance Drawer

Class: `.rebalance-drawer`

```
width: 280px (flex: 0 0 280px)
bg: var(--bg-sidebar)
border: 1px solid var(--border-tv)
radius: 8px
```

Inner content font: `12px Inter`.
Panel title: `12px, weight 600, uppercase, letter-spacing 0.05em`.

---

## AG Grid

Class applied: `finance-grid` (styled in `ag-grid-finance.css`).

Key values:
- Header bg: `rgba(13, 110, 253, 0.07)`, border-bottom `rgba(13, 110, 253, 0.25)`
- Header text: `#0d6efd`, `11px uppercase`
- Row even: `var(--bg-row-even)`, odd: `var(--bg-row-odd)`
- Row hover: `var(--bg-row-hover)`, selected: `var(--bg-row-selected)`
- Border color: `var(--border-grid)` / `var(--border-row)`
- Body font: `12.5px` or `13px`
- Radius: `6px`

---

## KPI Badges

Source: `ag-grid-finance.css`. Used in secondary KPI rows inside asset sections.

### `.kpi-badge` — Metric pill

```
bg: var(--bg-panel)  |  border: 1px solid var(--border-main)
radius: 20px  |  padding: 5px 10px
layout: inline-flex, space-between
```

Sub-elements:

| Class | Size | Weight | Notes |
|---|---|---|---|
| `.kpi-badge__label` | `0.6rem` | 500 | uppercase, letter-spacing 0.06em |
| `.kpi-badge__value` | `0.78rem` | 600 | tabular-nums |
| `.kpi-badge__unit` | `0.58rem` | 400 | `var(--text-muted)` |

### `.kpi-badge--with-spark` — Badge with inline sparkline

Width `auto` to accommodate the embedded chart.

### `.kpi-badge--action` — Ghost pill button (e.g. "Edit Tags")

```
bg: none  |  border: 1px solid var(--border-main)  |  radius: 20px
font: 0.72rem, var(--text-secondary)  |  padding: 3px 10px
```

---

## Filter Bar Container

Class: `.workspace-filter-bar` (source: `layout.css`)

```
display: flex  |  flex-wrap: nowrap  |  gap: 8px  |  padding: 7px
border-top + border-bottom: 1px solid var(--border-tv)
bg: var(--bg-filter-bar)  |  margin-bottom: 8px
```

### `.tv-vert-divider` — Vertical separator within the filter bar

```
width: 1px  |  height: 18px  |  bg: var(--border-tv)
```

Used between filter bar sections (timeframe strip, tag filter, buttons, rebalance toggle).

---

## Top Utility Button

Class: `.top-util-btn` (source: `layout.css`)

```
bg: transparent  |  border: none  |  radius: 4px
color: var(--text-muted)  |  padding: 4px 8px
hover: color var(--text-primary)
```

Used for icon-only utility actions in the top navbar (privacy toggle, settings, etc.).

---

## Modals

### Edit Tags Modal — `.ws-modal-*` (source: `components.css`)

Custom overlay modal (not Bootstrap). Key classes:

| Class | Role |
|---|---|
| `.ws-modal-overlay` | Full-screen backdrop |
| `.ws-modal-card` | Modal content card, `radius: 8px` |
| `.ws-modal-header` | Header row with title + close |
| `.ws-modal-title` | `13px, weight 600` |
| `.ws-modal-close` | Ghost close button |
| `.ws-modal-body` | Scrollable body |
| `.ws-modal-label` | Field label, `11px uppercase` |
| `.ws-modal-footer` | Footer with action buttons |
| `.ws-modal-dropdown` | Styled `dcc.Dropdown` inside the modal |

### Settings Modal — `.settings-modal` (source: `components.css`)

Bootstrap modal variant with custom overrides:

| Class | Role |
|---|---|
| `.settings-modal` | Scoping class on the `dbc.Modal` |
| `.settings-modal-body` | Body padding and layout |

Dark mode overrides applied via `html[data-theme="dark"] .settings-modal`.
