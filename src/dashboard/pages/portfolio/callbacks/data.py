"""
Data callbacks — page load and daily movers pagination.
These callbacks fetch from the database and populate the main page containers.
"""
from dash import Output, Input, State, callback
from dash.exceptions import PreventUpdate

from ..components.organisms.kpi_row import kpi_row
from ..components.organisms.asset_table import asset_table
from ..charts.portfolio_charts import daily_movers_table
from ..tabs import portfolio_tab_content, risk_tab_content, opportunities_tab_content
from ....controllers.portfolio_controller import PortfolioController


# ── 1. Initial page load ──────────────────────────────────────────

@callback(
    Output("portfolio_page_asset_store", "data"),
    Output("portfolio_kpi_container", "children"),
    Output("portfolio_page_asset_table_container", "children"),
    Output("tab-portfolio-content", "children"),
    Output("workspace-table-statusbar", "children"),
    Output("tab-risk-content", "children"),
    Output("tab-opportunities-content", "children"),
    Output("workspace-tag-filter", "options"),
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
    tag_options = [{"label": t, "value": t} for t in view_model.get("available_tags", [])]

    return (
        cached_data,
        kpi_row(view_model.get("kpi", {})),
        asset_table(rows),
        portfolio_tab_content(view_model, current_theme, kpi_data=view_model.get("kpi", {})),
        asset_count,
        risk_tab_content(view_model, current_theme, kpi_data=view_model.get("kpi", {})),
        opportunities_tab_content(view_model, current_theme, kpi_data=view_model.get("kpi", {})),
        tag_options,
    )


