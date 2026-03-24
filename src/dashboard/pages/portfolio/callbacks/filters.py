"""
Filter callbacks — timeframe selector and tag filter.
Both re-render tabs/table when the user changes the active filter.
"""
from dash import Output, Input, State, callback, no_update
from dash.exceptions import PreventUpdate

from ..components.organisms.kpi_row import kpi_row
from ..components.organisms.asset_table import asset_table
from ..tabs import portfolio_tab_content, risk_tab_content, opportunities_tab_content
from ._helpers import (
    _date_window,
    _filter_vm_by_timeframe,
    _fetch_snapshots,
    _fetch_asset_metadata,
    _build_compare_rows,
    _VALUATION_METRICS,
    _RISK_METRICS,
    _OPPS_METRICS,
)


# ── 3. Timeframe change → update KPIs + all tabs ──────────────────

@callback(
    Output("portfolio_kpi_container", "children", allow_duplicate=True),
    Output("tab-portfolio-content", "children", allow_duplicate=True),
    Output("workspace-timeframe", "data"),
    Output("tab-risk-content", "children", allow_duplicate=True),
    Output("tab-opportunities-content", "children", allow_duplicate=True),
    Output("asset-detail-sections", "children", allow_duplicate=True),
    Output("risk-asset-detail-sections", "children", allow_duplicate=True),
    Output("opportunities-asset-detail-sections", "children", allow_duplicate=True),
    Input("workspace-timeframe-selector", "value"),
    State("portfolio_page_asset_store", "data"),
    State("workspace-selected-asset", "data"),
    State("theme-store", "data"),
    prevent_initial_call=True,
)
def on_timeframe_change(timeframe, cached_data, selected_assets, theme):
    if not timeframe:
        raise PreventUpdate

    current_theme = theme or "light"
    start_date, end_date = _date_window(timeframe)
    kpi_children   = no_update
    portfolio_tab  = no_update
    risk_tab       = no_update
    opportunities_tab = no_update

    if cached_data:
        view_model = cached_data.get("view_model", {})
        kpi_children      = kpi_row(view_model.get("kpi", {}))
        filtered_vm       = _filter_vm_by_timeframe(view_model, start_date, end_date)
        portfolio_tab     = portfolio_tab_content(filtered_vm, current_theme, kpi_data=view_model.get("kpi", {}))
        risk_tab          = risk_tab_content(filtered_vm, current_theme, kpi_data=view_model.get("kpi", {}))
        opportunities_tab = opportunities_tab_content(filtered_vm, current_theme, kpi_data=view_model.get("kpi", {}))

    tickers = selected_assets if isinstance(selected_assets, list) else []
    if not tickers:
        return (
            kpi_children,
            portfolio_tab, timeframe, risk_tab, opportunities_tab,
            no_update, no_update, no_update,
        )

    snapshots = _fetch_snapshots(tickers, start_date, end_date)
    asset_rows = (cached_data or {}).get("view_model", {}).get("asset_table", {}).get("rows", [])
    names_map = {r["ticker"]: r.get("name", "") for r in asset_rows if r.get("ticker")}
    selected_row_objs = [r for r in asset_rows if r.get("ticker") in tickers]
    metadata_map = _fetch_asset_metadata(selected_row_objs)

    return (
        kpi_children,
        portfolio_tab, timeframe, risk_tab, opportunities_tab,
        _build_compare_rows(snapshots, _VALUATION_METRICS, current_theme, ns="val", names_map=names_map, metadata_map=metadata_map),
        _build_compare_rows(snapshots, _RISK_METRICS,      current_theme, ns="risk", names_map=names_map, metadata_map=metadata_map),
        _build_compare_rows(snapshots, _OPPS_METRICS,      current_theme, ns="opps", names_map=names_map, metadata_map=metadata_map),
    )


# ── 3b. Custom date filter → update KPIs + all tabs ──────────────

@callback(
    Output("portfolio_kpi_container", "children", allow_duplicate=True),
    Output("tab-portfolio-content", "children", allow_duplicate=True),
    Output("workspace-timeframe", "data", allow_duplicate=True),
    Output("tab-risk-content", "children", allow_duplicate=True),
    Output("tab-opportunities-content", "children", allow_duplicate=True),
    Output("asset-detail-sections", "children", allow_duplicate=True),
    Output("risk-asset-detail-sections", "children", allow_duplicate=True),
    Output("opportunities-asset-detail-sections", "children", allow_duplicate=True),
    Output("workspace-timeframe-selector", "value", allow_duplicate=True),
    Input("workspace-apply-filter-btn", "n_clicks"),
    State("workspace-start-date", "date"),
    State("workspace-end-date", "date"),
    State("portfolio_page_asset_store", "data"),
    State("workspace-selected-asset", "data"),
    State("theme-store", "data"),
    prevent_initial_call=True,
)
def on_date_filter_apply(n_clicks, start_date, end_date, cached_data, selected_assets, theme):
    if not n_clicks:
        raise PreventUpdate
    if not start_date or not end_date:
        raise PreventUpdate
    if start_date > end_date:
        raise PreventUpdate

    current_theme = theme or "light"
    kpi_children = no_update
    portfolio_tab = no_update
    risk_tab = no_update
    opportunities_tab = no_update

    if cached_data:
        view_model = cached_data.get("view_model", {})
        kpi_children = kpi_row(view_model.get("kpi", {}))
        filtered_vm = _filter_vm_by_timeframe(view_model, start_date, end_date)
        portfolio_tab = portfolio_tab_content(filtered_vm, current_theme, kpi_data=view_model.get("kpi", {}))
        risk_tab = risk_tab_content(filtered_vm, current_theme, kpi_data=view_model.get("kpi", {}))
        opportunities_tab = opportunities_tab_content(filtered_vm, current_theme, kpi_data=view_model.get("kpi", {}))

    tickers = selected_assets if isinstance(selected_assets, list) else []
    if not tickers:
        return (
            kpi_children,
            portfolio_tab, None, risk_tab, opportunities_tab,
            no_update, no_update, no_update, None,
        )

    snapshots = _fetch_snapshots(tickers, start_date, end_date)
    asset_rows = (cached_data or {}).get("view_model", {}).get("asset_table", {}).get("rows", [])
    names_map = {r["ticker"]: r.get("name", "") for r in asset_rows if r.get("ticker")}
    selected_row_objs = [r for r in asset_rows if r.get("ticker") in tickers]
    metadata_map = _fetch_asset_metadata(selected_row_objs)

    return (
        kpi_children,
        portfolio_tab, None, risk_tab, opportunities_tab,
        _build_compare_rows(snapshots, _VALUATION_METRICS, current_theme, ns="val", names_map=names_map, metadata_map=metadata_map),
        _build_compare_rows(snapshots, _RISK_METRICS,      current_theme, ns="risk", names_map=names_map, metadata_map=metadata_map),
        _build_compare_rows(snapshots, _OPPS_METRICS,      current_theme, ns="opps", names_map=names_map, metadata_map=metadata_map),
        None,
    )


# ── 3c. Tag filter → update asset table ──────────────────────────

@callback(
    Output("portfolio_page_asset_table_container", "children", allow_duplicate=True),
    Output("workspace-table-statusbar", "children", allow_duplicate=True),
    Input("workspace-tag-filter", "value"),
    State("portfolio_page_asset_store", "data"),
    prevent_initial_call=True,
)
def on_tag_filter_change(selected_tags, cached_data):
    if not cached_data:
        raise PreventUpdate

    rows = cached_data.get("view_model", {}).get("asset_table", {}).get("rows", [])
    if selected_tags:
        rows = [r for r in rows if any(t in r.get("tags", []) for t in selected_tags)]

    asset_count = f"{len(rows)} assets" if rows else "No assets"
    return asset_table(rows), asset_count
