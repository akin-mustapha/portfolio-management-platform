"""
Selection callbacks — asset row selection, compare mode, winners/losers sort,
asset profile tab population.
"""
from dash import ALL, MATCH, Output, Input, State, callback, ctx
from dash.exceptions import PreventUpdate

from .components.kpis import secondary_asset_kpi_row, secondary_asset_tag_row
from .charts.portfolio_charts import _ranked_panel
from ...controllers.asset_profile_controller import AssetProfileController
from ...controllers.portfolio_controller import PortfolioController
from ._callback_helpers import (
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
    snapshots    = _fetch_snapshots(tickers, start_date, end_date)
    names_map    = {r["ticker"]: r.get("name", "") for r in selected_rows if r.get("ticker")}
    metadata_map = _fetch_asset_metadata(selected_rows)

    return (
        tickers,
        _build_compare_rows(snapshots, _VALUATION_METRICS, current_theme, ns="val",  names_map=names_map, metadata_map=metadata_map),
        _build_compare_rows(snapshots, _RISK_METRICS,      current_theme, ns="risk", names_map=names_map, metadata_map=metadata_map),
        _build_compare_rows(snapshots, _OPPS_METRICS,      current_theme, ns="opps", names_map=names_map, metadata_map=metadata_map),
    )


# ── 2b. Pattern-matched collapse toggle for asset sections ─────────

@callback(
    Output({"type": "asset-section-collapse", "index": MATCH}, "is_open"),
    Input({"type": "asset-section-toggle",   "index": MATCH}, "n_clicks"),
    State({"type": "asset-section-collapse", "index": MATCH}, "is_open"),
    prevent_initial_call=True,
)
def toggle_asset_section(n, is_open):
    return not is_open if n else is_open


# ── 4. Winners/Losers sort toggle ────────────────────────────────

@callback(
    Output("winners-table", "children", allow_duplicate=True),
    Output("losers-table",  "children", allow_duplicate=True),
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
        _ranked_panel(losers,  sort_by, False),
    )


# ── 6. Asset Profile tab — populate on row selection (read-only) ──

@callback(
    Output("profile-ticker",           "children"),
    Output("profile-name",             "children"),
    Output("profile-description",      "children"),
    Output("profile-created",          "children"),
    Output("profile-last-ingestion",   "children"),
    Output("profile-summary-tags",     "children"),
    Output("profile-summary-category", "children"),
    Output("profile-summary-industry", "children"),
    Output("profile-summary-sector",   "children"),
    Input("portfolio-asset-table", "selectedRows"),
    prevent_initial_call=True,
)
def on_asset_profile_selected(selected_rows):
    if not selected_rows:
        raise PreventUpdate

    asset_row = selected_rows[0]
    vm = AssetProfileController().get_profile(asset_row)

    current_tags = vm.get("current_tags", [])
    tag_display  = ", ".join(current_tags) if current_tags else "—"

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
