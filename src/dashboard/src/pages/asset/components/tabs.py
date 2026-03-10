from ..components.charts import PriceStructurePlotlyLineChart, AssetValuePlotlyLineChart, RiskContextPlotlyLineChart, DCABiasPlotlyLineChart

from .....src.components.cards import card

from dash import dcc, html, Input, Output, callback, State

from ..components.tables import asset_table

import dash_bootstrap_components as dbc


# ─────────────────────────────────────────────
# Tabs
# ─────────────────────────────────────────────
def assets_tab(df):
    return card("Assets", asset_table(df), className='mb-4')

# Duplicate logic. Needed
# Might want to move graphs
def chart_tab(data, theme="light"):
    return html.Div([

        dbc.Row([
            dbc.Col(dcc.Graph(id="price_graph", figure=PriceStructurePlotlyLineChart().render(data, theme=theme), config={"displayModeBar": False}), md=6),
            dbc.Col(dcc.Graph(id="value_graph", figure=AssetValuePlotlyLineChart().render(data, theme=theme), config={"displayModeBar": False}), md=6)
        ], className="mb-3"),


        dbc.Row([
            dbc.Col(dcc.Graph(id="risk_graph", figure=RiskContextPlotlyLineChart().render(data, theme=theme), config={"displayModeBar": False}), md=6),
            dbc.Col(dcc.Graph(id="dca_graph", figure=DCABiasPlotlyLineChart().render(data, theme=theme), config={"displayModeBar": False}), md=6)
        ], className="mb-3"),

        # dbc.Row([
        #     dbc.Col(dcc.Graph(id="drawdown_graph", figure=RecentHeighDrawdownOverTimePlotlyLineChart().render(data)), md=6),
        # ])
    ], id="asset_page_chart_tab")

def chart_tab_empty():
    return html.Div([
        html.Div(
            "Select an asset to view charts.",
            className="text-muted text-center py-5",
            style={"fontSize": "1rem"}
        )
    ], id="asset_page_chart_tab")
