from datetime import date, timedelta

import dash_bootstrap_components as dbc
from dash import MATCH, Output, Input, State, callback, dcc, html, no_update
from dash.exceptions import PreventUpdate

from .components.kpis import kpi_row
from .components.tables import asset_table
from .components.workspace_tabs import (
    portfolio_tab_content,
    risk_tab_content,
    opportunities_tab_content,
)
from .components.asset_charts import (
    PriceStructurePlotlyLineChart,
    AssetValuePlotlyLineChart,
    ProfitRangePlotlyLineChart,
    RiskContextPlotlyLineChart,
    DCABiasPlotlyLineChart,
)
from .components.charts import _ranked_panel, daily_movers_table
from ...controllers.portfolio_controller import PortfolioController
from ...controllers.asset_controller import AssetController
from ...controllers.asset_profile_controller import AssetProfileController
from ...presenters.portfolio_presenter import PortfolioPresenter


# ── Timeframe → date window helper ───────────────────────────────

_TIMEFRAME_DAYS = {
    "1D": 1,
    "1W": 7,
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


def _filter_vm_by_timeframe(view_model: dict, start: str, end: str) -> dict:
    vm = dict(view_model)
    for key in ("portfolio_value_series", "portfolio_pnl_series", "portfolio_drawdown"):
        series = vm.get(key)
        if not series or not series.get("dates"):
            continue
        mask = [start <= d <= end for d in series["dates"]]
        vm[key] = {k: [v for v, m in zip(vals, mask) if m] for k, vals in series.items()}
    return vm


# ── Compare layout helpers ────────────────────────────────────────

_GRAPH_CONFIG = {"displayModeBar": False}

_ASSET_MODIFIERS    = ["asset-1", "asset-2", "asset-3"]
_ASSET_COLORS_LIGHT = {"asset-1": "#0d6efd", "asset-2": "#26a671", "asset-3": "#ef5350"}
_ASSET_COLORS_DARK  = {"asset-1": "#639aff", "asset-2": "#4cbb9f", "asset-3": "#f47c7c"}

_VALUATION_METRICS = [
    ("Price", PriceStructurePlotlyLineChart),
    ("Asset Value", AssetValuePlotlyLineChart),
    ("Profit Range (30D)", ProfitRangePlotlyLineChart),
]
_RISK_METRICS = [
    ("Risk Context", RiskContextPlotlyLineChart),
]
_OPPS_METRICS = [
    ("DCA Bias", DCABiasPlotlyLineChart),
]


def _fetch_snapshots(tickers, start_date, end_date):
    ctrl = AssetController()
    return [(t, ctrl.get_asset_snapshot(t.lower(), start_date, end_date)) for t in tickers]


def _build_compare_rows(snapshots, metrics, theme, ns="", names_map=None):
    """
    Build one tv-section-container per asset, placed side by side.
    Each container has a collapsible header (ticker) and charts stacked
    vertically inside. Pattern-matched IDs handle the collapse toggle.

    snapshots : list of (ticker, history) tuples
    metrics   : list of (title, ChartClass) tuples
    ns        : namespace prefix to make IDs unique across tabs
    names_map : optional dict mapping ticker -> display name
    Returns   : html.Div containing a dbc.Row of section containers.
    """
    n = len(snapshots)
    col_width = 12 // n
    color_map = _ASSET_COLORS_DARK if theme == "dark" else _ASSET_COLORS_LIGHT
    cols = []
    for asset_idx, (ticker, history) in enumerate(snapshots):
        modifier = _ASSET_MODIFIERS[asset_idx] if asset_idx < len(_ASSET_MODIFIERS) else "asset-1"
        accent   = color_map[modifier]
        idx = f"{ns}-{ticker}" if ns else ticker
        name = (names_map or {}).get(ticker, "")
        charts = []
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
        cols.append(dbc.Col(
            html.Div([
                html.Div(
                    header_children,
                    id={"type": "asset-section-toggle", "index": idx},
                    className=f"tv-section-header tv-section-header--{modifier}",
                    n_clicks=0,
                    style={"cursor": "pointer"},
                ),
                dbc.Collapse(
                    id={"type": "asset-section-collapse", "index": idx},
                    is_open=True,
                    children=html.Div(charts),
                ),
            ], className=f"tv-section-container tv-section-container--{modifier}"),
            width=col_width,
        ))
    return html.Div(dbc.Row(cols, className="g-2"))


# ── 1. Initial page load ──────────────────────────────────────────

@callback(
    Output("portfolio_page_asset_store", "data"),
    Output("portfolio_kpi_container", "children"),
    Output("portfolio_page_asset_table_container", "children"),
    Output("tab-portfolio-content", "children"),
    Output("workspace-table-footer", "children"),
    Output("tab-risk-content", "children"),
    Output("tab-opportunities-content", "children"),
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
        portfolio_tab_content(view_model, current_theme, kpi_data=view_model.get("kpi", {})),
        asset_count,
        risk_tab_content(view_model, current_theme),
        opportunities_tab_content(view_model, current_theme),
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
    names_map = {r["ticker"]: r.get("name", "") for r in selected_rows if r.get("ticker")}

    return (
        tickers,
        _build_compare_rows(snapshots, _VALUATION_METRICS, current_theme, ns="val", names_map=names_map),
        _build_compare_rows(snapshots, _RISK_METRICS, current_theme, ns="risk", names_map=names_map),
        _build_compare_rows(snapshots, _OPPS_METRICS, current_theme, ns="opps", names_map=names_map),
    )


# ── 2b. Pattern-matched collapse toggle for asset sections ─────────

@callback(
    Output({"type": "asset-section-collapse", "index": MATCH}, "is_open"),
    Input({"type": "asset-section-toggle", "index": MATCH}, "n_clicks"),
    State({"type": "asset-section-collapse", "index": MATCH}, "is_open"),
    prevent_initial_call=True,
)
def toggle_asset_section(n, is_open):
    return not is_open if n else is_open


# ── 3. Timeframe change → update KPIs + charts ───────────────────

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
    kpi_children = no_update
    portfolio_tab = no_update
    risk_tab = no_update
    opportunities_tab = no_update

    if cached_data:
        view_model = cached_data.get("view_model", {})
        kpi_children = kpi_row(view_model.get("kpi", {}))
        filtered_vm = _filter_vm_by_timeframe(view_model, start_date, end_date)
        portfolio_tab = portfolio_tab_content(filtered_vm, current_theme, kpi_data=view_model.get("kpi", {}))
        risk_tab = risk_tab_content(filtered_vm, current_theme)
        opportunities_tab = opportunities_tab_content(filtered_vm, current_theme)

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

    return (
        kpi_children,
        portfolio_tab, timeframe, risk_tab, opportunities_tab,
        _build_compare_rows(snapshots, _VALUATION_METRICS, current_theme, ns="val", names_map=names_map),
        _build_compare_rows(snapshots, _RISK_METRICS, current_theme, ns="risk", names_map=names_map),
        _build_compare_rows(snapshots, _OPPS_METRICS, current_theme, ns="opps", names_map=names_map),
    )


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

    presenter = PortfolioPresenter()
    winners = presenter._top_winner_bar_vm(assets, sort_by=sort_by)
    losers = presenter._top_losers_bar_vm(assets, sort_by=sort_by)

    return (
        _ranked_panel(winners, sort_by, True),
        _ranked_panel(losers, sort_by, False),
    )


# ── 5. Advanced filter toggle ─────────────────────────────────────

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


# ── 5a. Portfolio section toggle ──────────────────────────────────

@callback(
    Output("portfolio-charts-collapse", "is_open"),
    Input("portfolio-section-header", "n_clicks"),
    State("portfolio-charts-collapse", "is_open"),
    prevent_initial_call=True,
)
def toggle_portfolio_section(n, is_open):
    if n:
        return not is_open
    return is_open


# ── 5c. Risk tab — portfolio section toggle ───────────────────────

@callback(
    Output("risk-portfolio-charts-collapse", "is_open"),
    Input("risk-portfolio-section-header", "n_clicks"),
    State("risk-portfolio-charts-collapse", "is_open"),
    prevent_initial_call=True,
)
def toggle_risk_portfolio_section(n, is_open):
    if n:
        return not is_open
    return is_open


# ── 5e. Opportunities tab — portfolio section toggle ──────────────

@callback(
    Output("opportunities-portfolio-charts-collapse", "is_open"),
    Input("opportunities-portfolio-section-header", "n_clicks"),
    State("opportunities-portfolio-charts-collapse", "is_open"),
    prevent_initial_call=True,
)
def toggle_opportunities_portfolio_section(n, is_open):
    if n:
        return not is_open
    return is_open


# ── 6. Asset Profile tab — populate on row selection ─────────────

@callback(
    Output("profile-ticker", "children"),
    Output("profile-name", "children"),
    Output("profile-description", "children"),
    Output("profile-created", "children"),
    Output("profile-last-ingestion", "children"),
    Output("profile-tag-select", "options"),
    Output("profile-industry-select", "options"),
    Output("profile-sector-select", "options"),
    Output("profile-category-select", "options"),
    Output("profile-summary-tags", "children"),
    Output("profile-current-tags", "children"),
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
        vm["tag_options"],
        vm["industry_options"],
        vm["sector_options"],
        vm["category_options"],
        tag_display,
        "",  # profile-current-tags hidden
    )


# ── 7. Asset Profile tab — save classifications ───────────────────

@callback(
    Output("profile-save-status", "children"),
    Output("profile-summary-tags", "children", allow_duplicate=True),
    Input("profile-save-btn", "n_clicks"),
    State("profile-tag-select", "value"),
    State("profile-category-select", "value"),
    State("profile-category-select", "options"),
    State("profile-industry-select", "value"),
    State("profile-industry-select", "options"),
    State("profile-sector-select", "value"),
    State("profile-sector-select", "options"),
    State("portfolio-asset-table", "selectedRows"),
    prevent_initial_call=True,
)
def on_save_profile(n_clicks, tag_id, category_id, category_opts, industry_id, industry_opts, sector_id, sector_opts, selected_rows):
    if not selected_rows:
        raise PreventUpdate

    asset_row = selected_rows[0]
    asset_name = asset_row.get("name", "")
    messages = []

    if tag_id:
        msg = AssetProfileController().assign_tag(asset_name, tag_id)
        messages.append(msg)

    # Refresh tag display from service after save
    vm = AssetProfileController().get_profile(asset_row)
    current_tags = vm.get("current_tags", [])
    tag_display = ", ".join(current_tags) if current_tags else "—"

    status = " | ".join(messages) if messages else "Nothing to save."
    return status, tag_display


# ── 8. Daily movers pagination ────────────────────────────────────

@callback(
    Output("daily-movers-table", "children"),
    Input("daily-movers-n-dropdown", "value"),
    State("portfolio_page_asset_store", "data"),
    prevent_initial_call=True,
)
def on_daily_movers_n_change(n, cached_data):
    if not cached_data or not n:
        raise PreventUpdate
    movers = cached_data.get("view_model", {}).get("daily_movers", [])
    return daily_movers_table(movers, n=int(n))
