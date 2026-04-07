"""
Shared utilities used across portfolio callback modules.

Imported by: data.py, filters.py, selection.py, theme.py
"""

from datetime import date, timedelta

import dash_bootstrap_components as dbc
from dash import dcc, html

from ..components.atoms.badges import _kpi_badge
from ..components.organisms.secondary_kpi import (
    secondary_asset_kpi_row,
    secondary_asset_tag_row,
)
from ..charts.asset_charts import (
    PriceStructurePlotlyLineChart,
    AssetValuePlotlyLineChart,
    ProfitRangePlotlyLineChart,
    RiskContextPlotlyLineChart,
    DCABiasPlotlyLineChart,
    FXReturnAttributionDonutChart,
)
from ....controllers.asset_controller import AssetController
from ....controllers.asset_profile_controller import AssetProfileController

# ── Chart card builder ────────────────────────────────────────────


def _chart_card(card_id: str, label: str, fig) -> html.Div:
    """Single plotted chart card with a title and round close button."""
    return html.Div(
        [
            html.Div(
                [
                    html.Span(label, className="chart-card-title"),
                    html.Button(
                        "×",
                        id={"type": "close-chart-btn", "index": card_id},
                        className="chart-card-close-btn",
                        n_clicks=0,
                        title="Remove chart",
                    ),
                ],
                className="chart-card-header",
            ),
            dcc.Graph(
                figure=fig,
                config=_GRAPH_CONFIG,
                style={"height": "240px"},
            ),
        ],
        id={"type": "chart-card", "index": card_id},
        className="chart-card",
    )


# ── KPI badge helpers ─────────────────────────────────────────────


def _fmt_signed(v, fmt=".2f"):
    if v is None:
        return "—", 0
    sign = 1 if v > 0 else (-1 if v < 0 else 0)
    return f"{v:{fmt}}", sign


def _draggable(badge, metric_key):
    """Wrap a KPI badge in a draggable div so JS can pick up the metric key."""
    return html.Div(
        badge,
        draggable="true",
        **{"data-metric": metric_key},
        className="draggable-kpi",
    )


def _kpi_groups(row: dict):
    """Build Position and Risk badge lists from a raw asset table row."""
    value = row.get("value")
    profit = row.get("profit")
    pnl_pct = row.get("pnl_pct")
    cum_ret = row.get("cumulative_value_return")
    daily_ret = row.get("daily_value_return")
    weight = row.get("weight_pct")
    dca = row.get("dca_bias")
    drawdown = row.get("value_drawdown_pct_30d")
    volatility = row.get("volatility_30d")
    var_95 = row.get("var_95_1d")
    fx_impact = row.get("fx_impact")
    beta = row.get("beta_60d")
    asset_sharpe = row.get("asset_sharpe_ratio_30d")

    profit_str, profit_sign = _fmt_signed(profit, ",.2f")
    pnl_str, pnl_sign = _fmt_signed(pnl_pct, ".2f")
    ret_str, ret_sign = _fmt_signed(cum_ret, ".2f")
    daily_ret_str, daily_ret_sign = _fmt_signed(
        daily_ret * 100 if daily_ret is not None else None, ".2f"
    )
    dca_str, dca_sign = _fmt_signed(dca, ".3f")
    sharpe_str, sharpe_sign = _fmt_signed(asset_sharpe, ".2f")
    drawdown_str, drawdown_sign = _fmt_signed(
        drawdown * 100 if drawdown is not None else None, ".1f"
    )
    fx_str, fx_sign = _fmt_signed(fx_impact, ",.2f")

    position = [
        _draggable(
            _kpi_badge("Value", f"£{value:,.2f}" if value is not None else "—"),
            "asset_value",
        ),
        _draggable(
            _kpi_badge("P&L", f"£{profit_str}", change_sign=profit_sign),
            "asset_profit",
        ),
        _kpi_badge("P&L %", f"{pnl_str}%", change_sign=pnl_sign),
        _draggable(
            _kpi_badge("Return", f"{ret_str}%", change_sign=ret_sign),
            "asset_return",
        ),
        _draggable(
            _kpi_badge("Daily Ret", f"{daily_ret_str}%", change_sign=daily_ret_sign),
            "asset_daily_return",
        ),
        _kpi_badge("Weight", f"{weight:.2f}%" if weight is not None else "—"),
    ]
    risk = [
        _draggable(
            _kpi_badge("DCA Bias", dca_str, change_sign=dca_sign),
            "asset_dca_bias",
        ),
        _draggable(
            _kpi_badge("Drawdown", f"{drawdown_str}%", change_sign=drawdown_sign),
            "asset_risk",
        ),
        _kpi_badge("Vol 30D", f"{volatility:.4f}" if volatility is not None else "—"),
        _kpi_badge(
            "VaR 95%",
            f"£{var_95:,.2f}" if var_95 is not None else "—",
            change_sign=-1,
        ),
        _kpi_badge("Beta 60D", f"{beta:.2f}" if beta is not None else "—"),
        _kpi_badge("Sharpe 30D", sharpe_str, change_sign=sharpe_sign),
        _draggable(
            _kpi_badge("FX Impact", f"£{fx_str}", change_sign=fx_sign),
            "asset_fx_attribution",
        ),
    ]
    return position, risk


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

_KNOWN_NS = {"val", "risk", "opps"}
_ASSET_MODIFIERS = ["asset-1", "asset-2", "asset-3"]
_ASSET_COLORS_LIGHT = {"asset-1": "#0d6efd", "asset-2": "#26a671", "asset-3": "#ef5350"}
_ASSET_COLORS_DARK = {"asset-1": "#639aff", "asset-2": "#4cbb9f", "asset-3": "#f47c7c"}

# Metric groups shown in each tab's asset compare section
_VALUATION_METRICS = [
    ("Price", PriceStructurePlotlyLineChart),
    ("Asset Value", AssetValuePlotlyLineChart),
    ("Profit Range (30D)", ProfitRangePlotlyLineChart),
    ("FX Attribution", FXReturnAttributionDonutChart),
]
_RISK_METRICS = [
    ("Risk Context", RiskContextPlotlyLineChart),
]
_OPPS_METRICS = [
    ("DCA Bias", DCABiasPlotlyLineChart),
]


# ── Portfolio return ──────────────────────────────────────────────


def _compute_portfolio_return(pv: dict, start_date: str, end_date: str):
    """Filter and normalise portfolio_value_series into a % return series."""
    if not pv.get("dates"):
        return None
    result = {"dates": [], "values": []}
    for d, v, c in zip(pv["dates"], pv["values"], pv.get("costs", [])):
        if start_date <= str(d) <= end_date and c and c > 0:
            result["dates"].append(d)
            result["values"].append((v - c) / c * 100)
    return result or None


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
        vm[key] = {
            k: [v for v, m in zip(vals, mask) if m] for k, vals in series.items()
        }
    return vm


# ── Data fetching ─────────────────────────────────────────────────


def _fetch_snapshots(tickers: list, start_date: str, end_date: str) -> list:
    ctrl = AssetController()
    return [
        (t, ctrl.get_asset_snapshot(t.lower(), start_date, end_date)) for t in tickers
    ]


def _fetch_asset_metadata(selected_rows: list) -> dict:
    """Return full per-asset profile dict for each selected row."""
    result = {}
    ctrl = AssetProfileController()
    for row in selected_rows or []:
        ticker = row.get("ticker", "")
        if ticker:
            vm = ctrl.get_profile(row)
            result[ticker] = {
                "tags": vm.get("current_tags", []),
                "industry": vm.get("industry") or "—",
                "sector": vm.get("sector") or "—",
                "name": vm.get("name", ""),
                "description": vm.get("description", ""),
                "created": vm.get("created", "—"),
                "last_ingestion": vm.get("last_ingestion", "—"),
                "price": (
                    round(row["price"], 2) if row.get("price") is not None else None
                ),
                "avg_price": (
                    round(row["avg_price"], 2)
                    if row.get("avg_price") is not None
                    else None
                ),
            }
    return result


# ── Compare layout builder ────────────────────────────────────────


def _prop_cell(label: str, value: str) -> html.Div:
    """Inline identity prop — renders value directly (no callback target)."""
    return html.Div(
        [
            html.Div(label, className="prop-label"),
            html.Div(value or "—", className="prop-value"),
        ],
        className="profile-summary-prop",
    )


def _build_compare_rows(
    snapshots,
    theme,
    ns="",
    names_map=None,
    metadata_map=None,
    default_charts=None,
    rows_map=None,
):
    """
    Build one tv-section-container per asset, placed side by side.

    For ns="val" (Asset Profile tab): renders full unified card —
    identity (n=1 only), classification, tags, KPI groups, then chart zone.
    For other namespaces: renders the compact card (header + price + chart zone).

    snapshots      : list of (ticker, history) tuples
    ns             : namespace prefix; "val" triggers the full unified layout
    names_map      : optional dict mapping ticker -> display name
    metadata_map   : optional dict mapping ticker -> profile metadata
    default_charts : optional dict mapping ticker -> (metric_key, label, fig)
    rows_map       : optional dict mapping ticker -> raw asset table row
    """
    n = len(snapshots)
    col_width = 12 // n
    color_map = _ASSET_COLORS_DARK if theme == "dark" else _ASSET_COLORS_LIGHT
    cols = []

    for asset_idx, (ticker, history) in enumerate(snapshots):
        modifier = (
            _ASSET_MODIFIERS[asset_idx]
            if asset_idx < len(_ASSET_MODIFIERS)
            else "asset-1"
        )

        accent = color_map[modifier]
        idx = f"{ns}-{ticker}" if ns else ticker
        name = (names_map or {}).get(ticker, "")
        metadata = (metadata_map or {}).get(ticker, {})
        row_data = (rows_map or {}).get(ticker, {})

        # ── Default chart ──────────────────────────────────────────
        default_chart_info = (default_charts or {}).get(ticker)
        if default_chart_info:
            def_key, def_label, def_fig = default_chart_info
            initial_cards = [_chart_card(f"{idx}--{def_key}", def_label, def_fig)]
        else:
            initial_cards = []

        # ── Chart drop zone ────────────────────────────────────────
        charts = [
            html.Div(
                [
                    html.Span(
                        "Drag a metric badge here to plot",
                        id={"type": "asset-drop-hint", "index": idx},
                        className="chart-drop-zone__hint",
                    ),
                    html.Div(
                        id={"type": "asset-charts-grid", "index": idx},
                        className="asset-charts-grid",
                        children=initial_cards,
                    ),
                ],
                className="chart-drop-zone",
            ),
        ]

        # ── Header ─────────────────────────────────────────────────
        header_children = [ticker.upper(), html.Span("›", className="tv-chevron")]
        if name:
            header_children.append(html.Span(name, className="asset-header-name"))

        # ── Build card body ────────────────────────────────────────
        card_children = [
            html.Div(
                header_children,
                id={"type": "asset-section-toggle", "index": idx},
                className=f"tv-section-header tv-section-header--{modifier}",
                n_clicks=0,
                style={"cursor": "pointer"},
            ),
        ]

        if ns == "val":
            # ── Identity row ────────────────────────────────────────
            card_children.append(
                dbc.Row(
                    [
                        dbc.Col(_prop_cell("Name", metadata.get("name")), width=4),
                        dbc.Col(
                            _prop_cell("Description", metadata.get("description")),
                            width=4,
                        ),
                        dbc.Col(
                            _prop_cell("First Seen", metadata.get("created")),
                            width=2,
                        ),
                        dbc.Col(
                            _prop_cell(
                                "Last Ingestion", metadata.get("last_ingestion")
                            ),
                            width=2,
                        ),
                    ],
                    className="g-2 mb-3",
                )
            )

            # ── Classification badges ───────────────────────────────
            card_children.append(
                html.Div(
                    [
                        _kpi_badge("Industry", metadata.get("industry") or "—"),
                        _kpi_badge("Sector", metadata.get("sector") or "—"),
                    ],
                    className="kpi-badge-row mb-2",
                )
            )

            # ── Tags + Edit Tags ────────────────────────────────────
            card_children.append(
                secondary_asset_tag_row(ticker, metadata, accent=accent)
            )

            # ── KPI groups ─────────────────────────────────────────
            position_badges, risk_badges = (
                _kpi_groups(row_data) if row_data else ([], [])
            )
            card_children += [
                html.Hr(className="tv-divider"),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    "Position", className="profile-kpi-group-label"
                                ),
                                html.Div(
                                    position_badges,
                                    className="kpi-badge-row profile-kpi-group",
                                ),
                            ],
                            width=6,
                            style={"minWidth": 0},
                        ),
                        dbc.Col(
                            [
                                html.Div("Risk", className="profile-kpi-group-label"),
                                html.Div(
                                    risk_badges,
                                    className="kpi-badge-row profile-kpi-group",
                                ),
                            ],
                            width=6,
                            style={"minWidth": 0},
                        ),
                    ],
                    className="g-2 mb-2",
                ),
                html.Hr(className="tv-divider"),
            ]

        # ── Price/AVG Price + collapsible chart zone ───────────────
        card_children += [
            secondary_asset_kpi_row(ticker, metadata),
            dbc.Collapse(
                id={"type": "asset-section-collapse", "index": idx},
                is_open=True,
                children=html.Div(charts),
            ),
        ]

        cols.append(
            dbc.Col(
                html.Div(
                    card_children,
                    className=f"tv-section-container tv-section-container--{modifier}",
                ),
                width=col_width,
            )
        )
    return html.Div(dbc.Row(cols, className="g-2"))
