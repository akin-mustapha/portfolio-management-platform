# Theme System

---

## How It Works

The dashboard supports light and dark mode. Theme state flows through three layers:

**1. Store** — `dcc.Store(id="theme-store")` holds the current value: `"light"` or `"dark"`.

**2. CSS toggle** — A clientside callback in `theme.py` sets `data-theme` on `<html>`:
```js
document.documentElement.setAttribute('data-theme', theme);
```
This activates the `html[data-theme="dark"]` CSS block in `theme.css`.

**3. Chart patch** — A server callback (`update_chart_theme` in `theme.py`) patches Plotly figure backgrounds:
```python
bg = "#1e222d" if is_dark else "white"
fc = "#9598a1" if is_dark else "#555555"
p["layout"]["paper_bgcolor"] = bg
p["layout"]["plot_bgcolor"]  = bg
p["layout"]["font"]["color"] = fc
```

**Anti-FOUC** — `app.index_string` in `app.py` reads `localStorage['theme-store']` before first paint and applies `data-theme` immediately, preventing a white flash on dark mode reload.

---

## Bootstrap Base

```python
dbc.themes.COSMO   # loaded in app.py
```

All Bootstrap overrides are applied via CSS variable inheritance and `html[data-theme="dark"]` selectors in `theme.css`.

---

## Python-Side Color Constants

These are the only places colors may be hardcoded in Python:

**`src/dashboard/pages/portfolio/callbacks/_helpers.py`**
```python
_ASSET_COLORS_LIGHT = {"asset-1": "#0d6efd", "asset-2": "#26a671", "asset-3": "#ef5350"}
_ASSET_COLORS_DARK  = {"asset-1": "#639aff", "asset-2": "#4cbb9f", "asset-3": "#f47c7c"}
```
Used to pass `accent_color` to chart classes. Selected by `color_map = _ASSET_COLORS_DARK if theme == "dark" else _ASSET_COLORS_LIGHT`.

**`src/dashboard/pages/portfolio/callbacks/theme.py`**
```python
bg = "#1e222d" if is_dark else "white"
fc = "#9598a1" if is_dark else "#555555"
```
Used only to patch Plotly layout on theme change.

---

## Privacy Mode

A separate `dcc.Store(id="privacy-store")` holds `True/False`.
When active, `data-privacy="true"` is set on `<html>`, which blurs KPI values:
```css
html[data-privacy="true"] .kpi-value,
html[data-privacy="true"] .kpi-change,
html[data-privacy="true"] .kpi-unit {
  filter: blur(8px);
  user-select: none;
}
```

`user-select: none` prevents text selection while blurred (copy-paste would otherwise reveal the value).

---

## Adding a New Chart

When a new `dcc.Graph` is added to the dashboard, it **must** be wired into `update_chart_theme` in `theme.py` — otherwise it will retain stale colors when the user toggles theme. Add its component ID as an `Output` and return a `patch()` for it.
