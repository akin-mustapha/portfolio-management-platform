import dash_bootstrap_components as dbc
from src.dashboard.src.components.kpi import kpi_row
from src.dashboard.src.components.cards import card
from src.dashboard.src.components.charts.portfolio import portfolio_performance_chart
from dash import dcc, html

from src.dashboard.src.components.tables.portfolio import portfolio_timeseries_table


def portfolio_layout(df):
    return html.Div(
      [
        kpi_row(df),
        dbc.Row(
        [
          dbc.Col(
              card("Performance", dcc.Graph(
                  figure=portfolio_performance_chart(df),
                  config={'displayModeBar': False},
                  # id='controls-and-graph',
                  # style={'height':"100%"}
              )),
              # width="auto",
              className="mt-4",
          ),
          dbc.Col(
              card("History", portfolio_timeseries_table(df)),
              width="auto",
              className="mt-4",
          ),
        ]
        ),
      ]
    )