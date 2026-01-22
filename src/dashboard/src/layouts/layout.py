from dotenv import load_dotenv 
import os

from dash import Input, Output, dcc, html, callback
import dash_bootstrap_components as dbc
from src.shared.database.client import SQLModelClient
from src.services.ingestion_service.infrastructure.repositories.query_repository import SnapshotSQLQueryRepository
from src.dashboard.src.layouts.portfolio import portfolio_layout
from src.dashboard.src.layouts.asset import asset_layout
from src.dashboard.src.services.portfolio_service import PortfolioService
from src.dashboard.src.services.asset_service import AssetService
from src.dashboard.src.layouts.sidebar import content, sidebar




load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
database_client = SQLModelClient(database_url=DATABASE_URL)

# repo
name = 'asset_snapshot'
repo = SnapshotSQLQueryRepository(database_client)

# extraction
portfolio_profit = PortfolioService(repo).get_unrealized_profit()
asset_data = AssetService(repo).get_asset()




@callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
  if pathname == "/":
    return html.P("This is the content of the home page!")
  elif pathname == "/portfolio":
    return portfolio_layout(portfolio_profit)
  elif pathname == "/asset":
    return asset_layout(asset_data)
  # If the user tries to reach a different page, return a 404 message
  return html.Div(
    [
      html.H1("404: Not found", className="text-danger"),
      html.Hr(),
      html.P(f"The pathname {pathname} was not recognised..."),
    ],
    className="p-3 bg-light rounded-3",
  )

# Layout
layout = html.Div(
  [
    
    dcc.Location(id="url"), sidebar, content
    
  ])
