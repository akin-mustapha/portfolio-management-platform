
from dash import Output, Input, callback, State
from dash.exceptions import PreventUpdate

from .components.kpis import kpi_row
from ...controllers.portfolio_controller import PortfolioController
from .components.charts import performance_chart, value_chart, pnl_chart
from .components.tables import asset_table


@callback(
    Output("portfolio_page_asset_store", "data"),
    Output("portfolio_page_charts_container", "children"),
    Output("portfolio_page_asset_table_container", "children"),
    Output("portfolio_page_value_chart_container", "children"),
    Output("portfolio_page_pnl_chart_container", "children"),
    Output("portfolio_kpi_container", "children"),
    Input("portfolio_page_location", "pathname"),
    State("portfolio_page_asset_store", "data"),
    State("theme-store", "data"),
)
def load_portfolio_page(pathname, cached_data, theme):
    if pathname != "/portfolio":
        raise PreventUpdate
    # Decide data source
    cached_data = cached_data or {}
    view_model = cached_data.get("view_model", None)
    if view_model is None:
        view_model = PortfolioController().get_data()
        cached_data.update({"view_model": view_model})
    if view_model is None:
        raise PreventUpdate

    current_theme = theme or "light"

    # Compose UI (policy layer)
    charts = [
        performance_chart(view_model.get("asset_table", {}).get("rows", []), theme=current_theme)
        # other charts go here
    ]
    table = asset_table(view_model.get("asset_table", {}).get("rows", []))
    # Return state + UI
    return (
        cached_data,
        charts,
        table,
        value_chart(view_model.get("portfolio_value_series", {}), theme=current_theme),
        pnl_chart(view_model.get("portfolio_pnl_series", {}), theme=current_theme),
        kpi_row(view_model.get("kpi", {}))
    )
