from src.services.ingestion_service.infrastructure.repositories.query_repository import ItemSQLQueryRepository
from src.services.ingestion_service.infrastructure.repositories.entity_repository import EntityRepository
from src.shared.database.client import SQLModelClient
from dotenv import load_dotenv 
import os

from dash import Dash, html, dcc
import dash_ag_grid as dag
import plotly.express as px
import pandas as pd

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
database_client = SQLModelClient(database_url=DATABASE_URL)

repo = EntityRepository('asset_snapshot', database_client)

# data = repo.select({'id':1})
data = repo.select_all()

if type(data) == list:
  data = [dict(d._mapping) for d in data]
  data_df = pd.DataFrame(data)
  # print(data_df)
else:
  data = dict(data._mapping)
  data_df = pd.DataFrame(data)
  
# Initialize the app
app = Dash(__name__)

# App Layout
app.layout = html.Div([
  html.Div(children="Hello World"),
  dag.AgGrid(
    rowData=data,
    columnDefs=[{'field': k} for k in data[0].keys()]
  ),
  dcc.Graph(figure=px.histogram(data_df, x='asset_id', y='profit', histfunc='avg'))
  ])

# Run the app
if __name__ == "__main__":

  # print(data)

  # for i in data_df:
  #   print(i)

  #   break
  app.run(debug=True)