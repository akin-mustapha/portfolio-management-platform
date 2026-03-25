"""
Selection callbacks — asset row selection, compare mode, winners/losers sort.
"""

from dash import ALL, MATCH, Output, Input, State, callback, clientside_callback, ctx, no_update, html
from dash.exceptions import PreventUpdate

from ..components.atoms.badges import _kpi_badge
from ..charts.portfolio_charts import _ranked_panel, PortfolioPerformanceScatterPlot
from ..charts.asset_charts import (
    AssetValuePlotlyLineChart,
    ProfitRangePlotlyLineChart,
    DCABiasPlotlyLineChart,
    AssetVsPortfolioReturnChart,
)
from ....controllers.asset_profile_controller import AssetProfileController
from ....controllers.portfolio_controller import PortfolioController
from ._helpers import (
    _date_window,
    _fetch_snapshots,
    _fetch_asset_metadata,
    _build_compare_rows,
    _VALUATION_METRICS,
    _RISK_METRICS,
    _OPPS_METRICS,
)

# ── 2. Asset row selection → populate asset detail sections ───────


@callback(
    Output("workspace-selected-asset", "data"),
    Output("asset-detail-sections", "children"),
    Output("risk-asset-detail-sections", "children"),
    Output("opportunities-asset-detail-sections", "children"),
    Input("portfolio-asset-table", "selectedRows"),
    State("workspace-timeframe", "data"),
    State("theme-store", "data"),
    prevent_initial_call=True,
)
def on_asset_row_selected(selected_rows, timeframe, theme):
    if not selected_rows:
        return [], None, None, None

    tickers = [r.get("ticker") for r in selected_rows if r.get("ticker")][:3]
    if not tickers:
        raise PreventUpdate

    current_theme = theme or "light"
    start_date, end_date = _date_window(timeframe or "1Y")
    snapshots = _fetch_snapshots(tickers, start_date, end_date)
    names_map = {
        r["ticker"]: r.get("name", "") for r in selected_rows if r.get("ticker")
    }
    metadata_map = _fetch_asset_metadata(selected_rows)

    return (
        tickers,
        _build_compare_rows(
            snapshots,
            _VALUATION_METRICS,
            current_theme,
            ns="val",
            names_map=names_map,
            metadata_map=metadata_map,
        ),
        _build_compare_rows(
            snapshots,
            _RISK_METRICS,
            current_theme,
            ns="risk",
            names_map=names_map,
            metadata_map=metadata_map,
        ),
        _build_compare_rows(
            snapshots,
            _OPPS_METRICS,
            current_theme,
            ns="opps",
            names_map=names_map,
            metadata_map=metadata_map,
        ),
    )


# ── 2a. Chart click → programmatic row selection ──────────────────


@callback(
    Output("portfolio-asset-table", "selectedRows"),
    Input({"type": "chart-mover-row", "index": ALL}, "n_clicks"),
    Input("position_weight_donut_chart", "clickData"),
    State("portfolio_page_asset_store", "data"),
    prevent_initial_call=True,
)
def on_chart_click(mover_clicks, donut_click, cached_data):
    triggered = ctx.triggered_id

    if isinstance(triggered, dict) and triggered.get("type") == "chart-mover-row":
        if not any(mover_clicks):
            raise PreventUpdate
        ticker = triggered["index"]
    elif triggered == "position_weight_donut_chart":
        if not donut_click:
            raise PreventUpdate
        ticker = donut_click["points"][0].get("label")
    else:
        raise PreventUpdate

    if not ticker:
        raise PreventUpdate

    rows = (
        (cached_data or {}).get("view_model", {}).get("asset_table", {}).get("rows", [])
    )
    matching = [r for r in rows if r.get("ticker") == ticker]
    return matching if matching else no_update


# ── 2b. Pattern-matched collapse toggle for asset sections ─────────


@callback(
    Output({"type": "asset-section-collapse", "index": MATCH}, "is_open"),
    Input({"type": "asset-section-toggle", "index": MATCH}, "n_clicks"),
    State({"type": "asset-section-collapse", "index": MATCH}, "is_open"),
    prevent_initial_call=True,
)
def toggle_asset_section(n, is_open):
    return not is_open if n else is_open


# ── 4. Winners/Losers sort toggle ────────────────────────────────


@callback(
    Output("winners-table", "children", allow_duplicate=True),
    Output("losers-table", "children", allow_duplicate=True),
    Input("winners-losers-sort-toggle", "value"),
    State("portfolio_page_asset_store", "data"),
    prevent_initial_call=True,
)
def on_winners_losers_sort_change(sort_by, cached_data):
    if not cached_data:
        raise PreventUpdate

    assets = cached_data.get("view_model", {}).get("asset_table", {}).get("rows", [])
    if not assets:
        raise PreventUpdate

    winners, losers = PortfolioController().get_ranked_bars(assets, sort_by=sort_by)

    return (
        _ranked_panel(winners, sort_by, True),
        _ranked_panel(losers, sort_by, False),
    )


# ── 6. Asset Profile tab — populate metadata on row selection ──────


@callback(
    Output("profile-ticker", "children"),
    Output("profile-name", "children"),
    Output("profile-description", "children"),
    Output("profile-created", "children"),
    Output("profile-last-ingestion", "children"),
    Output("profile-summary-tags", "children"),
    Output("profile-summary-category", "children"),
    Output("profile-summary-industry", "children"),
    Output("profile-summary-sector", "children"),
    Input("portfolio-asset-table", "selectedRows"),
    prevent_initial_call=True,
)
def on_asset_profile_selected(selected_rows):
    if not selected_rows:
        raise PreventUpdate

    asset_row = selected_rows[0]
    vm = AssetProfileController().get_profile(asset_row)

    current_tags = vm.get("current_tags", [])
    tag_display = ", ".join(current_tags) if current_tags else "—"

    return (
        vm["ticker"],
        vm["name"],
        vm["description"],
        vm["created"],
        vm["last_ingestion"],
        tag_display,
        "—",  # category — assignment not yet implemented
        "—",  # industry — assignment not yet implemented
        "—",  # sector   — assignment not yet implemented
    )


# ── 7. Asset Profile — price/MA chart + snapshot strip ────────────


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


_DRAG_CHART_MAP = {
    "asset_value":    ("Asset Value",        AssetValuePlotlyLineChart),
    "asset_profit":   ("Profit Range (30D)", ProfitRangePlotlyLineChart),
    "asset_return":   ("Return vs Portfolio",AssetVsPortfolioReturnChart),
    "asset_dca_bias": ("DCA Bias",           DCABiasPlotlyLineChart),
}


@callback(
    Output("profile-snapshot-strip", "children"),
    Input("portfolio-asset-table", "selectedRows"),
    prevent_initial_call=True,
)
def on_asset_profile_deep_dive(selected_rows):
    if not selected_rows:
        raise PreventUpdate

    row = selected_rows[0]

    value   = row.get("value")
    profit  = row.get("profit")
    pnl_pct = row.get("pnl_pct")
    cum_ret = row.get("cumulative_value_return")
    weight  = row.get("weight_pct")
    dca     = row.get("dca_bias")

    profit_str, profit_sign = _fmt_signed(profit, ",.2f")
    pnl_str,    pnl_sign    = _fmt_signed(pnl_pct, ".2f")
    ret_str,    ret_sign    = _fmt_signed(cum_ret, ".2f")
    dca_str,    dca_sign    = _fmt_signed(dca, ".3f")

    return html.Div(
        [
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
            _kpi_badge("Weight", f"{weight:.2f}%" if weight is not None else "—"),
            _draggable(
                _kpi_badge("DCA Bias", dca_str, change_sign=dca_sign),
                "asset_dca_bias",
            ),
        ],
        className="kpi-badge-row",
    )


# ── 8. Drag-to-plot: render chart for dropped metric ──────────────

# Bridge: hidden button click → store the metric key from JS global.
clientside_callback(
    "function(n) { return window._droppedMetric || ''; }",
    Output("drop-metric-store", "data"),
    Input("_drop-btn", "n_clicks"),
    prevent_initial_call=True,
)


@callback(
    Output("chart-drop-zone-graph", "figure"),
    Output("chart-drop-zone-graph", "style"),
    Output("chart-drop-zone-hint", "style"),
    Output("chart-drop-zone-label", "children"),
    Input("drop-metric-store", "data"),
    State("portfolio-asset-table", "selectedRows"),
    State("workspace-timeframe", "data"),
    State("theme-store", "data"),
    State("portfolio_page_asset_store", "data"),
    prevent_initial_call=True,
)
def on_metric_drop(metric, selected_rows, timeframe, theme, cached_data):
    if not metric or not selected_rows:
        raise PreventUpdate

    chart_info = _DRAG_CHART_MAP.get(metric)
    if not chart_info:
        raise PreventUpdate

    row = selected_rows[0]
    ticker = row.get("ticker")
    if not ticker:
        raise PreventUpdate

    label, ChartClass = chart_info
    current_theme = theme or "light"
    start_date, end_date = _date_window(timeframe or "1Y")
    snapshots = _fetch_snapshots([ticker], start_date, end_date)
    snapshot = dict(snapshots).get(ticker, {})

    if metric == "asset_return":
        portfolio_return = {"dates": [], "values": []}
        pv = (cached_data or {}).get("view_model", {}).get("portfolio_value_series", {})
        if pv.get("dates"):
            for d, v, c in zip(pv["dates"], pv["values"], pv.get("costs", [])):
                if start_date <= str(d) <= end_date and c and c > 0:
                    portfolio_return["dates"].append(d)
                    portfolio_return["values"].append((v - c) / c * 100)
        data = {**snapshot, "portfolio_return": portfolio_return}
    else:
        data = snapshot

    fig = ChartClass().render(data, theme=current_theme)
    graph_style = {"height": "240px", "display": "block"}
    hint_style  = {"display": "none"}
    return fig, graph_style, hint_style, label


# ── 8. Scatter plot bubble highlight on row selection ─────────────


@callback(
    Output("portfolio_performance_map", "figure", allow_duplicate=True),
    Input("portfolio-asset-table", "selectedRows"),
    State("portfolio_page_asset_store", "data"),
    State("theme-store", "data"),
    prevent_initial_call=True,
)
def on_scatter_selection_highlight(selected_rows, cached_data, theme):
    if not cached_data:
        raise PreventUpdate

    distribution = cached_data.get("view_model", {}).get("position_distribution", [])
    tickers = [r["ticker"] for r in (selected_rows or []) if r.get("ticker")]

    return PortfolioPerformanceScatterPlot().render(
        distribution,
        theme=theme or "light",
        selected_tickers=tickers or None,
    )
