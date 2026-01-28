import dash_bootstrap_components as dbc
from dash import dcc, html, Output, Input, callback
from dash.exceptions import PreventUpdate
# ─────────────────────────────────────────────
# App imports
# ─────────────────────────────────────────────
from src.dashboard.src.components.kpi import kpi_row
from src.dashboard.src.components.cards import card
from src.dashboard.src.components.charts.portfolio import portfolio_performance_chart
from src.dashboard.src.pages.portfolio.charts import WinnersPlotlyBarChart, LosersPlotlyBarChart
from src.dashboard.src.pages.portfolio.tables import (
    asset_table,
)
from src.dashboard.src.services.asset_service import AssetService
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
def chart_tab(data):
    return html.Div([
        dbc.Row([
            dbc.Col(dcc.Graph(id="performance_chart", figure=portfolio_performance_chart().render(data)), md=6)
        ], className="mb-3"),

        dbc.Row([
            dbc.Col(dcc.Graph(id="winners_chart", figure=WinnersPlotlyBarChart().render(data)), md=6),
            dbc.Col(dcc.Graph(id="losers_chart", figure=LosersPlotlyBarChart().render(data)), md=6)
        ])
    ], id="portfolio_page_charts")
# ─────────────────────────────────────────────
# Page layout
# ─────────────────────────────────────────────
def portfolio_layout(df):
    return html.Div([
        dcc.Location(id="portfolio_page_location"),
        # KPIs
        kpi_row(df),
        dbc.Row([
            dbc.Col(
                asset_section(),
                # md=4,
                # className="mt-4",
            ),
        ]),
        # Main content
        dbc.Row([
            dbc.Col(
                id="portfolio_page_charts_container",
                children=chart_tab(df),
                # md=8,
                # className="mt-4",
            ),
        ]),
    ])
@callback(
    Output("portfolio_page_charts_container", "children"),
    Output("portfolio_page_asset_table_container", "children"),
    Input("portfolio_page_location", "pathname"),
)
def load_portfolio_page(pathname):
    # CONTROLLS DATA ACCESS LOGIC
    # DATA PROPERGATION 
    if pathname != "/portfolio":
        raise PreventUpdate
    df = AssetService.get_asset_data()
    if df.empty:
        raise PreventUpdate
    data = df.to_dict("records")
    return (
        data,
        # TODO: AGREE ON THE BEST INTERFACE FOR THE PARAMETER USED BY COMPONENTS
        asset_table(df),
        chart_tab(data)
    )