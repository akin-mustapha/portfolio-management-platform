# Sentiment & Status Colors

Used to communicate financial direction (gain/loss) and UI state (active/reduce/increase).

---

## Financial Sentiment

| Meaning | Light | Dark | Where |
|---|---|---|---|
| Positive / Gain | `#26a671` | `#4cbb9f` | AG Grid pnl columns, rebalance increase badge |
| Negative / Loss | `#ef5350` | `#f47c7c` | AG Grid pnl columns, rebalance reduce badge |
| Neutral teal (tags) | `#26a69a` | `#4db6ac` | `.profile-tag-chip` |

**Python constants** in `src/dashboard/pages/portfolio/components/organisms/asset_table.py`:
```python
POSITIVE_COLOR = "#26a671"
NEGATIVE_COLOR = "#ef5350"
```
Applied via AG Grid `styleConditions`:
```python
{"condition": "params.value > 0", "style": {"color": POSITIVE_COLOR, "fontWeight": "600"}},
{"condition": "params.value < 0", "style": {"color": NEGATIVE_COLOR, "fontWeight": "600"}},
```

---

## Rebalance Action Badges

Defined in `sidebar.css`. Classes: `.rebalance-action-increase` and `.rebalance-action-reduce`.

| Action | Background | Text |
|---|---|---|
| Increase | `rgba(38, 166, 113, 0.15)` | `#26a671` |
| Reduce | `rgba(239, 83, 80, 0.15)` | `#ef5350` |

Border-radius: `3px`. Font: `10px`, weight `700`, uppercase.

---

## Rebalance Slider

The allocation slider in the rebalance drawer uses:

- Track (rail) color: `var(--border-tv)` — `.rebalance-slider .dash-slider-track`
- Filled range color: `#0d6efd` (Bootstrap blue) — `.rebalance-slider .dash-slider-range`
- Thumb fill/border: `#0d6efd` light / `var(--asset-1-color-dark)` (`#639aff`) dark
- Thumb focus ring: `rgba(13, 110, 253, 0.15)`

---

## Primary Action Color

Used for: active nav item border/text, focus rings, theme toggle hover, AG Grid header text/border.

| Usage | Value |
|---|---|
| Nav active border + text | `#0d6efd` |
| AG Grid header text | `#0d6efd` |
| AG Grid header bg | `rgba(13, 110, 253, 0.07)` |
| AG Grid header border-bottom | `rgba(13, 110, 253, 0.25)` |
| Form focus ring color | `#0d6efd` |
| Form focus box-shadow | `rgba(13, 110, 253, 0.25)` |

---

## Asset Identity Colors (for chart lines and section accents)

See [tokens.md](./tokens.md) for the full `--asset-*` variable table.
Python maps in `_helpers.py` are the source when passing colors to Plotly charts.
