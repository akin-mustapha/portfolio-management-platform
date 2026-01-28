import dash_bootstrap_components as dbc
from dash import dcc, html, Output, Input, callback, State
from dash.exceptions import PreventUpdate
import pandas as pd
# ─────────────────────────────────────────────
# App imports
# ─────────────────────────────────────────────
from src.dashboard.src.components.kpi import kpi_row
from src.dashboard.src.components.cards import card
from src.dashboard.src.pages.portfolio.charts import WinnersPlotlyBarChart, LosersPlotlyBarChart, PortfolioPerformancePlotlyLineChart
from src.dashboard.src.pages.portfolio.tables import (
    asset_table,
)
from src.dashboard.src.services.asset_service import AssetService
from src.dashboard.src.services.portfolio_service import PortfolioService
# ──────────────────────────────────────────── ─
# Section builders
# ─────────────────────────────────────────────
# def performance_section(df):
#     return card(
#         "Performance",
#         dcc.Graph(
#             figure=WinnersPlotlyBarChart(),
#             config={"displayModeBar": False},
#         ),
#     )
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
# ─────────────────────────────────────────────
# Page layout
# ─────────────────────────────────────────────
def portfolio_layout(df):
    return html.Div([
        dcc.Location(id="portfolio_page_location"),
        dcc.Store(id="portfolio_page_asset_store"),
        # KPIs
        kpi_row(df),
        dbc.Row([
            dbc.Col(
                children=asset_section(),
                # md=4,
                # className="mt-4",
            ),
        ]),
        # Main content
        dbc.Row([
            dbc.Col(
                id="portfolio_page_value_chart_container",
                children=value_chart(),
                width="auto",
                md=12,
                    # className="mt-4",
                ),

        ]),
        html.Div(
            id="portfolio_page_charts_container",
            children=performance_chart(),
                # md=8,
                # className="mt-4",
            ),
    ])
@callback(
    Output("portfolio_page_asset_store", "data"),
    Output("portfolio_page_charts_container", "children"),
    Output("portfolio_page_asset_table_container", "children"),
    Output("portfolio_page_value_chart_container", "children"),
    Input("portfolio_page_location", "pathname"),
    State("portfolio_page_asset_store", "data"),
)
def load_portfolio_page(pathname, cached_data):
    if pathname != "/portfolio":
        raise PreventUpdate

    # Decide data source
    cached_data = dict()
    if cached_data.get("asset_data", None) is None:
        asset_data_df = AssetService.get_asset_data()
        asset_data_dict = asset_data_df.to_dict("records")
        cached_data.update({"asset_data": asset_data_dict })
    else:
        asset_data_df = pd.DataFrame(cached_data.get("asset_data", {}))
    
    if cached_data.get("portfolio_return_data", None) is None:
        return_data = PortfolioService().get_unrealized_profit()
        cached_data.update({"portfolio_return_data": return_data})
    else:
        return_data = cached_data.get("portfolio_return_data", {})

    if asset_data_df.empty:
        raise PreventUpdate

    # Compose UI (policy layer)
    charts = [
        performance_chart(asset_data_dict),
        # other charts go here
    ]

    table = asset_table(asset_data_dict)

    # Return state + UI
    return (
        cached_data,
        charts,
        table,
        value_chart(return_data)
    )