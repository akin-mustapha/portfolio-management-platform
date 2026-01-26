import dash_bootstrap_components as dbc
from src.dashboard.src.components.kpi import asset_kpi_row
from src.dashboard.src.components.cards import card
from src.dashboard.src.components.charts.asset import asset_chart
from dash import dcc, html

from src.dashboard.src.components.tables.asset import asset_table

from src.dashboard.src.styles.style import TAB_CONTENT_STYLE


assets = lambda df: html.Div([
  card("Assets", asset_table(df))
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
      # KPIs
      dbc.Row(
        [
          dbc.Col(asset_kpi_row(df), xs=12)
        ],
        className="mb-4"
      ),
      # Tabs
      dbc.Row(
        [
          dbc.Col(
            dbc.Tabs(
              [
                dbc.Tab(
                  assets(df),
                  label="Assets",
                  tab_class_name="px-3",
                  style=TAB_CONTENT_STYLE,
                ),
                dbc.Tab(
                  assets_monitoring(df),
                  label="Monitoring",
                  tab_class_name="px-3",
                  style=TAB_CONTENT_STYLE,
                ),
              ],
              className="mb-3",
            ),
            xs=12,
          )
        ]
      ),
    ],
    # fluid=True,
    # className="py-3 px-2 px-md-4",
  )