"""
Portfolio callbacks — entry point.

Imports all callback sub-modules so Dash registers every @callback decorator.
Add new callback files here as the feature set grows.

Sub-modules:
  data.py       → page load, daily movers
  filters.py    → timeframe selector, tag filter
  selection.py  → row selection, compare mode, asset profile
  tags.py       → edit tags modal (open / save / close)
  ui.py         → collapse toggles (no data dependency)
  theme.py      → theme/privacy toggles, chart re-theme, clientside resize
  settings.py   → settings modal and credential management
  rebalancing.py → rebalance panel toggle, config save, plan generation

Shared utilities (not callbacks):
  _helpers.py   → constants, date window, fetch, build compare rows
"""

from . import (  # noqa: F401
    data,  # noqa: F401
    filters,  # noqa: F401
    selection,  # noqa: F401
    tags,  # noqa: F401
    ui,  # noqa: F401
    theme,  # noqa: F401
    settings,  # noqa: F401
    rebalancing,  # noqa: F401
)

# Re-exported for portfolio_page.py: `from .callbacks import load_portfolio_page`
from .data import load_portfolio_page  # noqa: F401

# Re-exported for theme.py (same package — used via `from . import ...`)
from ._helpers import (  # noqa: F401
    _build_compare_rows,
    _date_window,
    _fetch_snapshots,
    _VALUATION_METRICS,
    _RISK_METRICS,
    _OPPS_METRICS,
)
