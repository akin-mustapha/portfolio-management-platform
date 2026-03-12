from datetime import date, timedelta

from dash import Output, Input, State, callback, html, no_update
from dash.exceptions import PreventUpdate

from .components.kpis import kpi_row
from .components.tables import asset_table
from .components.workspace_tabs import (
    portfolio_tab_content,
    valuation_tab_content,
)
from ...controllers.portfolio_controller import PortfolioController
from ...controllers.asset_controller import AssetController


# ── Timeframe → date window helper ───────────────────────────────

_TIMEFRAME_DAYS = {
    "1M": 30,
    "3M": 90,
    "6M": 180,
    "1Y": 365,
    "All": None,
}


def _date_window(timeframe):
    days = _TIMEFRAME_DAYS.get(timeframe)
    end = str(date.today())
    start = str(date.today() - timedelta(days=days)) if days else "2000-01-01"
    return start, end


# ── 1. Initial page load ──────────────────────────────────────────

@callback(
    Output("portfolio_page_asset_store", "data"),
    Output("portfolio_kpi_container", "children"),
    Output("portfolio_page_asset_table_container", "children"),
    Output("tab-portfolio-content", "children"),
    Output("workspace-table-footer", "children"),
    Input("portfolio_page_location", "pathname"),
    State("portfolio_page_asset_store", "data"),
    State("theme-store", "data"),
)
def load_portfolio_page(pathname, cached_data, theme):
    if pathname != "/portfolio":
        raise PreventUpdate

    cached_data = cached_data or {}
    view_model = cached_data.get("view_model", None)
    if view_model is None:
        view_model = PortfolioController().get_data()
        cached_data.update({"view_model": view_model})
    if view_model is None:
        raise PreventUpdate

    current_theme = theme or "light"
    rows = view_model.get("asset_table", {}).get("rows", [])
    asset_count = f"{len(rows)} assets" if rows else "No assets"

    return (
        cached_data,
        kpi_row(view_model.get("kpi", {})),
        asset_table(rows),
        portfolio_tab_content(view_model, current_theme),
        asset_count,
    )


# ── 2. Asset row selection → update Valuation tab ────────────────

@callback(
    Output("workspace-selected-asset", "data"),
    Output("workspace-chart-header", "children"),
    Output("tab-valuation-content", "children"),
    Input("portfolio-asset-table", "selectedRows"),
    State("workspace-timeframe", "data"),
    State("theme-store", "data"),
    prevent_initial_call=True,
)
def on_asset_row_selected(selected_rows, timeframe, theme):
    if not selected_rows:
        return no_update, "", valuation_tab_content()

    ticker = selected_rows[0].get("ticker", "")
    if not ticker:
        raise PreventUpdate

    current_theme = theme or "light"
    start_date, end_date = _date_window(timeframe or "1Y")

    asset_history = AssetController().get_asset_snapshot(ticker.lower(), start_date, end_date)

    header = html.Span(ticker.upper(), className="asset-ticker-tag")

    return (
        ticker,
        header,
        valuation_tab_content(asset_history, current_theme),
    )


# ── 3. Timeframe change → update KPIs + charts ───────────────────

@callback(
    Output("portfolio_kpi_container", "children", allow_duplicate=True),
    Output("tab-valuation-content", "children", allow_duplicate=True),
    Output("workspace-timeframe", "data"),
    Input("workspace-timeframe-selector", "value"),
    State("portfolio_page_asset_store", "data"),
    State("workspace-selected-asset", "data"),
    State("theme-store", "data"),
    prevent_initial_call=True,
)
def on_timeframe_change(timeframe, cached_data, selected_asset, theme):
    if not timeframe:
        raise PreventUpdate

    current_theme = theme or "light"

    # Update KPIs from cached portfolio data
    kpi_children = no_update
    if cached_data:
        view_model = cached_data.get("view_model", {})
        kpi_children = kpi_row(view_model.get("kpi", {}))

    # Update asset charts only if an asset is selected
    if not selected_asset:
        return kpi_children, no_update, timeframe

    start_date, end_date = _date_window(timeframe)
    asset_history = AssetController().get_asset_snapshot(selected_asset.lower(), start_date, end_date)

    return (
        kpi_children,
        valuation_tab_content(asset_history, current_theme),
        timeframe,
    )


# ── 4. Advanced filter toggle ────────────────────────────────────

@callback(
    Output("workspace-adv-filter-collapse", "is_open"),
    Input("workspace-adv-filter-btn", "n_clicks"),
    State("workspace-adv-filter-collapse", "is_open"),
    prevent_initial_call=True,
)
def toggle_advanced_filter(n, is_open):
    if n:
        return not is_open
    return is_open
