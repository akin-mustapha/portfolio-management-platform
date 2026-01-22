from src.services.ingestion_service.infrastructure.repositories.query_repository import SnapshotSQLQueryRepository
from src.services.ingestion_service.infrastructure.repositories.entity_repository import EntityRepository
from src.shared.database.client import SQLModelClient
from dotenv import load_dotenv 
import os

from dash import Dash, html, dcc, callback, Output, Input
import dash_ag_grid as dag
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
database_client = SQLModelClient(database_url=DATABASE_URL)

# repo
name = 'asset_snapshot'
repo = SnapshotSQLQueryRepository(database_client)

# extraction
top_10_profit = repo.select_top_10_profit_asset_snapshot()
portfolio_profit = repo.select_portfolio_unrealized_return()

# transformation
def prepare_data(data):
  if type(data) == list:
    data = [dict(d._mapping) for d in data]
    data_df = pd.DataFrame(data)
  else:
    data = dict(data._mapping)
    data_df = pd.DataFrame(data)
  return data_df
    
top_10_profit_df = prepare_data(top_10_profit)

# Columns
columnDefs = [
    {"field": "name"},
    {"field": "description"},
    {
        "field": "profit",
        "type": "numericColumn",
        "valueFormatter": {"function": "d3.format(',.2f')(params.value)"},
        "cellStyle": {
            "styleConditions": [
                {
                    "condition": "params.value > 0",
                    "style": {"color": "green"}
                },
                {
                    "condition": "params.value < 0",
                    "style": {"color": "red"}
                }
            ]
        }
    },
    {
        "field": "price",
        "valueFormatter": {"function": "d3.format(',.2f')(params.value)"}
    },
    {
        "field": "value",
        "valueFormatter": {"function": "d3.format(',.2f')(params.value)"}
    }
]

portfolio_profit = prepare_data(portfolio_profit)
portfolio_profit_columns = [
    {"field": "data_date"},
    {"field": "portfolio_value"},
    {
        "field": "unrealized_return",
        "type": "numericColumn",
        "valueFormatter": {"function": "d3.format(',.2f')(params.value)"},
        "cellStyle": {
            "styleConditions": [
                {
                    "condition": "params.value > 0",
                    "style": {"color": "green"}
                },
                {
                    "condition": "params.value < 0",
                    "style": {"color": "red"}
                }
            ]
        }
    }
]

# App
app = Dash(external_stylesheets=[dbc.themes.DARKLY])

# table
table = dbc.Table.from_dataframe(
    top_10_profit_df, striped=True, bordered=True, hover=True, index=True, size='sm'
)

# figure
fig = px.line(
  portfolio_profit,
  x='data_date',
  y='portfolio_value',
  )
fig.update_layout(
    template="plotly_dark",
    hovermode="x unified",
    margin=dict(l=20, r=20, t=40, b=20),
    title=None,
)
fig.update_traces(
    line=dict(width=3),
    mode="lines",
)
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=False)


# kpi
def kpi(title, value, color="primary"):
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="text-muted"),
            html.H3(value, className=f"text-{color}")
        ]),
        className="shadow-sm"
    )

# Layout
app.layout = html.Div(
   dbc.Container(
      children=[
        html.H2('Porfolio', className='fw-light mb-1'),
        dbc.Row(
          [
            dbc.Col(kpi("Portfolio Value", "€12,430", "white")),
            dbc.Col(kpi("Unrealized P&L", "+€1,240", "success")),
            dbc.Col(kpi("Realized P&L", "+€860", "success"))
          ],
          className="mb-4"
        ),
        dbc.Row(
        [
          dbc.Col(
            dbc.Card([
              dbc.CardHeader("Portfolio Performance"),
              dbc.CardBody(
                dcc.Graph(
                  figure=fig,
                  config={'displayModeBar': False},
                  id='controls-and-graph',
                  style={'height':"100%"}
                ), className='p-0'
            )], className="shadow-sm h-100 w-100"), width=6, className="d-flex" 
          ),
          dbc.Col(
             dbc.Card([
              dbc.CardHeader("Portfolio Performance"),
              dbc.CardBody(
                dag.AgGrid(
                  rowData=portfolio_profit.to_dict("records"),
                  columnDefs=portfolio_profit_columns,
                  style={'height':"100%"}
                  ), className='p-0'
                ) 
            ], className="shadow-sm h-100 w-100"), width=6, className="d-flex"  
          )
      ])
  ], 
      fluid=True,
      className="py-4"
      )
      )

if __name__ == "__main__":
    app.run(debug=True)