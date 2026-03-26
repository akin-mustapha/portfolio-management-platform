"""
Selection callbacks — asset row selection, compare mode, winners/losers sort.
"""

from dash import (
    ALL,
    MATCH,
    Output,
    Input,
    State,
    callback,
    clientside_callback,
    ctx,
    no_update,
)
from dash.exceptions import PreventUpdate

from ..tabs.tab_asset_profile import _empty_state

from ..components.atoms.badges import _kpi_badge
from ..charts.portfolio_charts import _ranked_panel, PortfolioPerformanceScatterPlot
from ..charts.asset_charts import (
    AssetValuePlotlyLineChart,
    ProfitRangePlotlyLineChart,
    DCABiasPlotlyLineChart,
    DailyReturnBarChart,
    AssetVsPortfolioReturnChart,
    RiskContextPlotlyLineChart,
    FXReturnAttributionDonutChart,
)
from ....controllers.portfolio_controller import PortfolioController
from ._helpers import (
    _date_window,
    _fetch_snapshots,
    _fetch_asset_metadata,
    _build_compare_rows,
    _chart_card,
    _fmt_signed,
    _draggable,
    _compute_portfolio_return,
    _KNOWN_NS,
    _ASSET_MODIFIERS,
    _ASSET_COLORS_DARK,
    _ASSET_COLORS_LIGHT,
)

# ── 2. Asset row selection → populate asset detail sections ───────


@callback(
    Output("workspace-selected-asset", "data"),
    Output("asset-detail-sections", "children"),
    Output("risk-asset-detail-sections", "children"),
    # Output("opportunities-asset-detail-sections", "children"),
    Input("portfolio-asset-table", "selectedRows"),
    State("workspace-timeframe", "data"),
    State("theme-store", "data"),
    State("portfolio_page_asset_store", "data"),
    prevent_initial_call=True,
)
def on_asset_row_selected(selected_rows, timeframe, theme, cached_data):
    if not selected_rows:
        return [], _empty_state(), []

    tickers = [r.get("ticker") for r in selected_rows if r.get("ticker")][:3]
    if not tickers:
        raise PreventUpdate

    current_theme = theme or "light"
    color_map = _ASSET_COLORS_DARK if current_theme == "dark" else _ASSET_COLORS_LIGHT
    start_date, end_date = _date_window(timeframe or "1Y")
    snapshots = _fetch_snapshots(tickers, start_date, end_date)
    names_map = {
        r["ticker"]: r.get("name", "") for r in selected_rows if r.get("ticker")
    }
    metadata_map = _fetch_asset_metadata(selected_rows)
    rows_map = {r["ticker"]: r for r in selected_rows if r.get("ticker")}

    # Build portfolio return series for relative performance chart (2+ assets)
    portfolio_return = None
    if len(tickers) >= 2:
        pv = (cached_data or {}).get("view_model", {}).get("portfolio_value_series", {})
        portfolio_return = _compute_portfolio_return(pv, start_date, end_date)

    # Pre-render default charts per ticker for val and risk sections
    val_default_charts = {}
    risk_default_charts = {}
    for i, (ticker, snapshot) in enumerate(snapshots):
        modifier = _ASSET_MODIFIERS[i] if i < len(_ASSET_MODIFIERS) else "asset-1"
        accent = color_map[modifier]
        if portfolio_return is not None:
            data = {**snapshot, "portfolio_return": portfolio_return}
            val_fig = AssetVsPortfolioReturnChart().render(
                data, theme=current_theme, accent_color=accent
            )
            val_default_charts[ticker] = ("asset_return", "Return vs Portfolio", val_fig)
        else:
            val_fig = ProfitRangePlotlyLineChart().render(
                snapshot, theme=current_theme, accent_color=accent
            )
            val_default_charts[ticker] = ("asset_profit", "Profit Range (30D)", val_fig)
        risk_fig = RiskContextPlotlyLineChart().render(
            snapshot, theme=current_theme, accent_color=accent
        )
        risk_default_charts[ticker] = ("asset_risk", "Risk Context", risk_fig)

    return (
        tickers,
        _build_compare_rows(
            snapshots,
            current_theme,
            ns="val",
            names_map=names_map,
            metadata_map=metadata_map,
            default_charts=val_default_charts,
            rows_map=rows_map,
        ),
        _build_compare_rows(
            snapshots,
            current_theme,
            ns="risk",
            names_map=names_map,
            metadata_map=metadata_map,
            default_charts=risk_default_charts,
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


# ── 7. Drag-to-plot: render chart for dropped metric ──────────────

_DRAG_CHART_MAP = {
    "asset_value": ("Asset Value", AssetValuePlotlyLineChart),
    "asset_profit": ("Profit Range (30D)", ProfitRangePlotlyLineChart),
    "asset_return": ("Return vs Portfolio", AssetVsPortfolioReturnChart),
    "asset_daily_return": ("Daily Return", DailyReturnBarChart),
    "asset_dca_bias": ("DCA Bias", DCABiasPlotlyLineChart),
    "asset_risk": ("Risk Context", RiskContextPlotlyLineChart),
    "asset_fx_attribution": ("FX Attribution", FXReturnAttributionDonutChart),
}

# Bridge: hidden button click → store the metric key from JS global.
clientside_callback(
    "function(n) { return window._droppedMetric || ''; }",
    Output("drop-metric-store", "data"),
    Input("_drop-btn", "n_clicks"),
    prevent_initial_call=True,
)


@callback(
    Output({"type": "asset-charts-grid", "index": ALL}, "children"),
    Input("drop-metric-store", "data"),
    State({"type": "asset-charts-grid", "index": ALL}, "children"),
    State("portfolio-asset-table", "selectedRows"),
    State("workspace-timeframe", "data"),
    State("theme-store", "data"),
    State("portfolio_page_asset_store", "data"),
    prevent_initial_call=True,
)
def on_metric_drop(metric, all_grid_children, selected_rows, timeframe, theme, cached_data):
    if not metric or not selected_rows:
        raise PreventUpdate

    chart_info = _DRAG_CHART_MAP.get(metric)
    if not chart_info:
        raise PreventUpdate

    tickers = [r.get("ticker") for r in selected_rows if r.get("ticker")][:3]
    if not tickers:
        raise PreventUpdate

    # Single ALL output → ctx.outputs_list is the flat list of matched dicts
    grid_ids = [o["id"]["index"] for o in ctx.outputs_list]
    if not grid_ids:
        raise PreventUpdate

    label, ChartClass = chart_info
    current_theme = theme or "light"
    color_map = _ASSET_COLORS_DARK if current_theme == "dark" else _ASSET_COLORS_LIGHT
    start_date, end_date = _date_window(timeframe or "1Y")
    snapshots = dict(_fetch_snapshots(tickers, start_date, end_date))

    portfolio_return = None
    if metric == "asset_return":
        pv = (cached_data or {}).get("view_model", {}).get("portfolio_value_series", {})
        portfolio_return = _compute_portfolio_return(pv, start_date, end_date)

    result = []

    for grid_idx, children in zip(grid_ids, all_grid_children):
        # Strip namespace prefix (e.g. "val-AIAIL" → "AIAIL")
        parts = grid_idx.split("-", 1)
        ticker = parts[1] if len(parts) == 2 and parts[0] in _KNOWN_NS else grid_idx

        if ticker not in tickers:
            result.append(no_update)
            continue

        # Duplicate guard — skip if this metric card already exists in the grid
        card_id = f"{grid_idx}--{metric}"
        existing_ids = [
            c.get("props", {}).get("id", {}).get("index")
            for c in (children or [])
            if isinstance(c, dict)
        ]
        if card_id in existing_ids:
            result.append(no_update)
            continue

        asset_i = tickers.index(ticker)
        modifier = _ASSET_MODIFIERS[asset_i] if asset_i < len(_ASSET_MODIFIERS) else "asset-1"
        accent = color_map[modifier]
        snapshot = snapshots.get(ticker, {})
        data = {**snapshot, "portfolio_return": portfolio_return} if metric == "asset_return" else snapshot
        fig = ChartClass().render(data, theme=current_theme, accent_color=accent)

        result.append(list(children or []) + [_chart_card(card_id, label, fig)])

    return result


@callback(
    Output({"type": "asset-charts-grid", "index": ALL}, "children", allow_duplicate=True),
    Input({"type": "close-chart-btn", "index": ALL}, "n_clicks"),
    State({"type": "asset-charts-grid", "index": ALL}, "children"),
    prevent_initial_call=True,
)
def on_close_chart(n_clicks_list, all_grid_children):
    if not any(n_clicks_list):
        raise PreventUpdate
    triggered = ctx.triggered_id
    if not isinstance(triggered, dict) or triggered.get("type") != "close-chart-btn":
        raise PreventUpdate

    btn_index = triggered["index"]           # e.g. "val-AIAIL--asset_profit"
    grid_idx = btn_index.rsplit("--", 1)[0]  # e.g. "val-AIAIL"

    grid_ids = [o["id"]["index"] for o in ctx.outputs_list]
    result = []

    for gid, children in zip(grid_ids, all_grid_children):
        if gid != grid_idx:
            result.append(no_update)
            continue
        new_children = [
            c for c in (children or [])
            if not (
                isinstance(c, dict)
                and c.get("props", {}).get("id", {}).get("index") == btn_index
            )
        ]
        result.append(new_children)

    return result


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
