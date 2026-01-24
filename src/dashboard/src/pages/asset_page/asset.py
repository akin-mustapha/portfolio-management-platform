import dash_bootstrap_components as dbc
from src.dashboard.src.components.kpi import asset_kpi_row
from src.dashboard.src.components.cards import card
from src.dashboard.src.components.charts.asset import asset_chart
from dash import dcc, html

from src.dashboard.src.components.tables.asset import asset_table
from src.dashboard.src.pages.asset_page.components.tag import tags

from src.dashboard.src.styles.style import TAB_CONTENT_STYLE


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
          # TODO: Column header tooltip
          # e.g
          # Definition: Measures the peak-to-trough decline in an asset’s value.
          # Formula: (Trough Value - Peak Value) / Peak Value
          # Interpretation: 
          #    - Negative values (e.g., -0.1) indicate a 10% decline from the peak.
          #    - Smaller negative numbers = smaller drawdowns (better)
          #    - Larger negative numbers = bigger drawdowns (riskier)

          dbc.Tab(assets(df), label="Assets", style=TAB_CONTENT_STYLE),
          dbc.Tab(assets_monitoring(df), label="Monitoring", style=TAB_CONTENT_STYLE),
          dbc.Tab(tags, label="Tag", style=TAB_CONTENT_STYLE)
        ]
        ),
    ],
    # fluid=True,
    # className="py-4"
  )