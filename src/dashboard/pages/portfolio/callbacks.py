"""
Portfolio callbacks — entry point.

Imports all callback sub-modules so Dash registers every @callback decorator.
Add new callback files here as the feature set grows.

Sub-modules:
  callbacks_data.py       → page load, daily movers
  callbacks_filters.py    → timeframe selector, tag filter
  callbacks_selection.py  → row selection, compare mode, asset profile
  callbacks_tags.py       → edit tags modal (open / save / close)
  callbacks_ui.py         → collapse toggles (no data dependency)

Shared utilities (not callbacks):
  _callback_helpers.py    → constants, date window, fetch, build compare rows
"""
from . import callbacks_data       # noqa: F401
from . import callbacks_filters    # noqa: F401
from . import callbacks_selection  # noqa: F401
from . import callbacks_tags       # noqa: F401
from . import callbacks_ui         # noqa: F401

# Re-exported for portfolio_page.py: `from .callbacks import load_portfolio_page`
from .callbacks_data import load_portfolio_page  # noqa: F401

# Re-exported for theme_callbacks.py: `from .callbacks import _build_compare_rows, ...`
from ._callback_helpers import (  # noqa: F401
    _build_compare_rows,
    _date_window,
    _fetch_snapshots,
    _VALUATION_METRICS,
    _RISK_METRICS,
    _OPPS_METRICS,
)
