from src.services.ingestion_service.infrastructure.repositories.query_repository import SnapshotSQLQueryRepository
from src.services.ingestion_service.infrastructure.repositories.entity_repository import EntityRepository
from src.shared.database.client import SQLModelClient
from dotenv import load_dotenv 
import os

from dash import Dash, html, dcc, callback, Output, Input
import dash_ag_grid as dag
import plotly.express as px
import pandas as pd

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
database_client = SQLModelClient(database_url=DATABASE_URL)

name = 'asset_snapshot'
repo = SnapshotSQLQueryRepository(database_client)

# data = repo.select({'id':1})
top_10_profit = repo.select_top_10_profit_asset_snapshot()

def prepare_data(data):
  if type(data) == list:
    data = [dict(d._mapping) for d in data]
    data_df = pd.DataFrame(data)
    # print(data_df)
  else:
    data = dict(data._mapping)
    data_df = pd.DataFrame(data)
  return data_df
    
top_10_profit_df = prepare_data(top_10_profit)
# Initialize the app
app = Dash(__name__)

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

# App Layout
app.layout = html.Div([
  html.Div(children=name,
          style={'textAlign': 'center', 'color': 'blue', 'fontSize': 30}),

  html.Hr(),
  html.Div(className='row', children=[
    dcc.RadioItems(options=['profit', 'value', 'price'], value='profit', id='controls-and-radio-item'),
  ]),
  html.H2(
    f"Total Profit: {top_10_profit_df['profit'].sum():,.2f}",
    style={"textAlign": "center"}
  ),
  html.Div(className='row', children=[
    dag.AgGrid(
      rowData=top_10_profit_df.to_dict("records"),
      columnDefs=columnDefs
    ),

  ]),
  html.Div(className='row', children=[
    dcc.Graph(figure={}, id='controls-and-graph')
  ], style={'height': 1000})
  ])

@callback(
  Output(component_id='controls-and-graph', component_property='figure'),
  Input(component_id='controls-and-radio-item', component_property='value')
)

def update_graph(col_chosen):
    fig = px.histogram(top_10_profit_df, x='name', y=col_chosen, histfunc='avg', height=800, width=1300)
    fig.update_layout(
    xaxis_title="Asset",
    yaxis_title=f"Avg {col_chosen.capitalize()}",
    template="plotly_dark",
    xaxis_tickangle=-45,
    margin=dict(l=40, r=40, t=40, b=20)
    )

    # fig.update_traces(marker_line_width=0)
    fig.update_traces(
    hovertemplate='<b>%{x}</b><br>' + f'{col_chosen}'
)
    return fig

# Run the app
if __name__ == "__main__":
  app.run(debug=True)