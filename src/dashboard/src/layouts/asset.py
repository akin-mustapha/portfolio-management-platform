import dash_bootstrap_components as dbc
from src.dashboard.src.components.kpi import kpi_row
from src.dashboard.src.components.cards import card
from src.dashboard.src.components.charts.asset import asset_chart
from dash import dcc

from src.dashboard.src.components.tables.asset import asset_table


def asset_layout(df):
    return dbc.Container(
      [
          kpi_row(df),
          dbc.Row(
              [
                  dbc.Col(
                      card("Performance", dcc.Graph(
                          figure=asset_chart(df),
                          config={'displayModeBar': False},
                          # id='controls-and-graph',
                          # style={'height':"100%"}
                      )),
                      width=6,
                      className="d-flex",
                  ),
                  dbc.Col(
                      card("History", asset_table(df)),
                      width=6,
                      className="d-flex",
                  ),
              ]
          ),
      ],
      fluid=True,
      className="py-4"
    )