import dash_bootstrap_components as dbc
from src.dashboard.src.components.kpi import asset_kpi_row
from src.dashboard.src.components.cards import card
from src.dashboard.src.components.charts.asset import asset_chart
from dash import dcc, html, callback

from src.dashboard.src.components.tables.asset import asset_table


btn_submit_tag_name = dbc.Button("Submit", id="btn-create-tag-name", color="primary")
                 
tags = html.Div([
  dbc.Row(
    [
      dbc.Col([
        dbc.Input(id='input-tag-name', placeholder="Enter tag name...", type="text", className="sm")

      ]),
      dbc.Col(btn_submit_tag_name, width="auto"),
    ]

  ),
  dbc.Row(
    [
      dbc.Col(html.Div(id="tag-create-status"), width="auto"),
    ]
    
  ),
])