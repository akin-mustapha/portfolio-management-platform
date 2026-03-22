"""
Shared utilities used across portfolio callback modules.

Imported by:
  callbacks_data.py, callbacks_filters.py, callbacks_selection.py,
  theme_callbacks.py (via callbacks.py re-export)
"""
from datetime import date, timedelta

import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.exceptions import PreventUpdate

from .components.kpis import secondary_asset_kpi_row, secondary_asset_tag_row
from .charts.asset_charts import (
    PriceStructurePlotlyLineChart,
    AssetValuePlotlyLineChart,
    ProfitRangePlotlyLineChart,
    RiskContextPlotlyLineChart,
    DCABiasPlotlyLineChart,
    FXReturnAttributionDonutChart,
)
from ...controllers.asset_controller import AssetController
from ...controllers.asset_profile_controller import AssetProfileController


# ── Constants ─────────────────────────────────────────────────────

_GRAPH_CONFIG = {"displayModeBar": False}

_TIMEFRAME_DAYS = {
    "1D": 1,
    "1W": 7,
    "1M": 30,
    "3M": 90,
    "6M": 180,
    "1Y": 365,
    "All": None,
}

_ASSET_MODIFIERS    = ["asset-1", "asset-2", "asset-3"]
_ASSET_COLORS_LIGHT = {"asset-1": "#0d6efd", "asset-2": "#26a671", "asset-3": "#ef5350"}
_ASSET_COLORS_DARK  = {"asset-1": "#639aff", "asset-2": "#4cbb9f", "asset-3": "#f47c7c"}

# Metric groups shown in each tab's asset compare section
_VALUATION_METRICS = [
    ("Price",               PriceStructurePlotlyLineChart),
    ("Asset Value",         AssetValuePlotlyLineChart),
    ("Profit Range (30D)",  ProfitRangePlotlyLineChart),
    ("FX Attribution",      FXReturnAttributionDonutChart),
]
_RISK_METRICS = [
    ("Risk Context", RiskContextPlotlyLineChart),
]
_OPPS_METRICS = [
    ("DCA Bias", DCABiasPlotlyLineChart),
]


# ── Date window ───────────────────────────────────────────────────

def _date_window(timeframe: str) -> tuple[str, str]:
    days = _TIMEFRAME_DAYS.get(timeframe)
    end = str(date.today())
    start = str(date.today() - timedelta(days=days)) if days else "2000-01-01"
    return start, end


def _filter_vm_by_timeframe(view_model: dict, start: str, end: str) -> dict:
    vm = dict(view_model)
    for key in ("portfolio_value_series", "portfolio_pnl_series", "portfolio_drawdown"):
        series = vm.get(key)
        if not series or not series.get("dates"):
            continue
        mask = [start <= d <= end for d in series["dates"]]
        vm[key] = {k: [v for v, m in zip(vals, mask) if m] for k, vals in series.items()}
    return vm


# ── Data fetching ─────────────────────────────────────────────────

def _fetch_snapshots(tickers: list, start_date: str, end_date: str) -> list:
    ctrl = AssetController()
    return [(t, ctrl.get_asset_snapshot(t.lower(), start_date, end_date)) for t in tickers]


def _fetch_asset_metadata(selected_rows: list) -> dict:
    """Return {ticker: {tags, industry, sector, price, avg_price}} for each selected row."""
    result = {}
    ctrl = AssetProfileController()
    for row in (selected_rows or []):
        ticker = row.get("ticker", "")
        if ticker:
            vm = ctrl.get_profile(row)
            result[ticker] = {
                "tags":      vm.get("current_tags", []),
                "industry":  "—",
                "sector":    "—",
                "price":     row.get("price"),
                "avg_price": row.get("avg_price"),
            }
    return result


# ── Compare layout builder ────────────────────────────────────────

def _build_compare_rows(
    snapshots,
    metrics,
    theme,
    ns="",
    names_map=None,
    metadata_map=None,
):
    """
    Build one tv-section-container per asset, placed side by side.
    Each container has a collapsible header (ticker) and charts stacked
    vertically inside. Pattern-matched IDs handle the collapse toggle.

    snapshots  : list of (ticker, history) tuples
    metrics    : list of (title, ChartClass) tuples
    ns         : namespace prefix to make IDs unique across tabs
    names_map  : optional dict mapping ticker -> display name
    """
    n = len(snapshots)
    col_width = 12 // n
    color_map = _ASSET_COLORS_DARK if theme == "dark" else _ASSET_COLORS_LIGHT
    cols = []
    for asset_idx, (ticker, history) in enumerate(snapshots):
        modifier = _ASSET_MODIFIERS[asset_idx] if asset_idx < len(_ASSET_MODIFIERS) else "asset-1"
        accent   = color_map[modifier]
        idx      = f"{ns}-{ticker}" if ns else ticker
        name     = (names_map or {}).get(ticker, "")
        charts   = []
        for i, (title, ChartClass) in enumerate(metrics):
            if i > 0:
                charts.append(html.Hr(className="tv-divider"))
            charts.append(html.Div([
                html.Div(title, className="tv-section-header"),
                dcc.Graph(
                    figure=ChartClass().render(history, theme, accent_color=accent),
                    config=_GRAPH_CONFIG,
                ),
            ]))
        header_children = [ticker.upper(), html.Span("›", className="tv-chevron")]
        if name:
            header_children.append(html.Span(name, className="asset-header-name"))
        metadata = (metadata_map or {}).get(ticker, {})
        cols.append(dbc.Col(
            html.Div([
                html.Div(
                    header_children,
                    id={"type": "asset-section-toggle", "index": idx},
                    className=f"tv-section-header tv-section-header--{modifier}",
                    n_clicks=0,
                    style={"cursor": "pointer"},
                ),
                secondary_asset_kpi_row(ticker, metadata),
                secondary_asset_tag_row(ticker, metadata, accent=accent),
                dbc.Collapse(
                    id={"type": "asset-section-collapse", "index": idx},
                    is_open=True,
                    children=html.Div(charts),
                ),
            ], className=f"tv-section-container tv-section-container--{modifier}"),
            width=col_width,
        ))
    return html.Div(dbc.Row(cols, className="g-2"))
