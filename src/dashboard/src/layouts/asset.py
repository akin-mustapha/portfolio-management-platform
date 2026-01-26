import dash_bootstrap_components as dbc
from src.dashboard.src.components.kpi import asset_kpi_row
from src.dashboard.src.components.cards import card
from src.dashboard.src.components.charts.asset import asset_chart
from dash import dcc, html

from src.dashboard.src.components.tables.asset import asset_table


assets = lambda df: html.Div([
  card("History", asset_table(df))
])
assets_monitoring = lambda df: html.Div([
    card("Performance", dcc.Graph(
            figure=asset_chart(df),
            config={'displayModeBar': False},
            # id='controls-and-graph',
            # style={'height':"100%"}
        )),
    
])
def asset_layout(df):
  return html.Div(
    [
      asset_kpi_row(df),
      dbc.Tabs(
        [
          dbc.Tab(assets(df), label="Assets"),
          dbc.Tab(assets_monitoring(df), label="Monitoring")
        ]
        ),
    ],
    # fluid=True,
    # className="py-4"
  )