import dash_bootstrap_components as dbc
from dash import dcc, html, Output, Input, callback, State
from dash.exceptions import PreventUpdate
# ─────────────────────────────────────────────
# App imports
# ─────────────────────────────────────────────
from src.dashboard.app.pages.portfolio.kpis import kpi_row
from src.dashboard.app.pages.portfolio.charts import WinnersPlotlyBarChart, LosersPlotlyBarChart, PortfolioPerformancePlotlyLineChart, PortfolioPNLPlotlyLineChart
from src.dashboard.app.pages.portfolio.tables import asset_table
from src.dashboard.app.controllers.portfolio_controller import PortfolioController
# ─────────────────────────────────────────────
# Section builders
# ─────────────────────────────────────────────
def asset_section():
    return html.Div(
        id="portfolio_page_asset_table_container",
        children=[asset_table(None)],
    )
# Duplicate logic. Needed
# Might want to move graphs - Open/Close Principle
def performance_chart(data=None):
    if data is None:
        return html.P("NO DATA")
    return dbc.Row([
        dbc.Col(dcc.Graph(id="winners_chart", figure=WinnersPlotlyBarChart().render(data)), md=6),
        dbc.Col(dcc.Graph(id="losers_chart", figure=LosersPlotlyBarChart().render(data)), md=6)
    ],  id="portfolio_page_charts")

def value_chart(data=None):
    if data is None:
        return html.P("NO DATA")
    return dcc.Graph(id="value_chart", figure=PortfolioPerformancePlotlyLineChart().render(data))


def pnl_chart(data=None):
    if data is None:
        return html.P("NO DATA")
    return dcc.Graph(id="pnl_char", figure=PortfolioPNLPlotlyLineChart().render(data))
# ─────────────────────────────────────────────
# Page layout
# ─────────────────────────────────────────────
def portfolio_layout():
    return html.Div([
        dcc.Location(id="portfolio_page_location"),
        dcc.Store(id="portfolio_page_asset_store"),
        # KPIs
        kpi_row(),
        dbc.Row([
            dbc.Col(
                children=asset_section(),
            ),
        ]),
        # Main content
        dbc.Row([
            dbc.Col(
                id="portfolio_page_value_chart_container",
                children=value_chart(),
                width="auto",
                md=6,
                ),
            dbc.Col(
                id="portfolio_page_pnl_chart_container",
                children=pnl_chart(),
                width="auto",
                md=6,
            )

        ]),
        html.Div(
            id="portfolio_page_charts_container",
            children=performance_chart(),
            ),
    ])
@callback(
    Output("portfolio_page_asset_store", "data"),
    Output("portfolio_page_charts_container", "children"),
    Output("portfolio_page_asset_table_container", "children"),
    Output("portfolio_page_value_chart_container", "children"),
    Output("portfolio_page_pnl_chart_container", "children"),
    Input("portfolio_page_location", "pathname"),
    State("portfolio_page_asset_store", "data"),
)
def load_portfolio_page(pathname, cached_data):
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
    # Compose UI (policy layer)
    charts = [
        performance_chart(view_model.get("asset_table", {}).get("rows", []))
        # other charts go here
    ]
    table = asset_table(view_model.get("asset_table", {}).get("rows", []))
    # Return state + UI
    
    return (
        cached_data,
        charts,
        table,
        value_chart(view_model.get("portfolio_value_series", {})),
        pnl_chart(view_model.get("portfolio_pnl_series", {}))
    )