from dotenv import load_dotenv 
import os

from dash import Input, Output, dcc, html, callback
import dash_bootstrap_components as dbc
from src.dashboard.src.pages.portfolio.portfolio_page import portfolio_layout
from src.dashboard.src.pages.asset.asset_page import asset_layout
from src.dashboard.src.pages.tag.tag_page import tag_layout
from src.dashboard.src.services.portfolio_service import PortfolioService
from src.dashboard.src.services.asset_service import AssetService
from src.dashboard.src.layouts.sidebar import content, sidebar
from src.services.tagging_service.application. tagging_service_builder import build_tagging_service

from src.dashboard.src.components.buttons import btn_side_toggle
# extraction
portfolio_profit = PortfolioService().get_unrealized_profit()
asset_metric = AssetService().get_asset_data()


@callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
  if pathname == "/portfolio":
    return portfolio_layout(portfolio_profit)
  elif pathname == "/assets":
    return asset_layout()
  elif pathname == "/tag":
    return tag_layout(asset_metric)
  # If the user tries to reach a different page, return a 404 message
  return html.Div(
    [
      html.H1("404: Not found", className="text-danger"),
      html.Hr(),
      html.P(f"The pathname {pathname} was not recognised..."),
    ],
    className="p-3 bg-light rounded-3",
  )

porfoltio_serivce = build_tagging_service()
from dash import callback, Input, Output, State, no_update
@callback(
    Output("tag-create-status", "value"),
    Input("btn-create-tag-name", "n_clicks"),
    State("input-tag-name", "value"),
    prevent_initial_call=True
)
def create_new_tag(n_clicks, value):
    if not value:
        return "⚠️ Tag name cannot be empty"

    porfoltio_serivce.create_tag(value)
    return f"✅ Tag '{value}' created"

# Layout
layout = dbc.Container(
  [
    ## Make sidebar collapsable
    dbc.Row([
        dbc.Col(
            btn_side_toggle,
            width="auto"
        )
    ], className="mb-2"),
    dbc.Row([
      dcc.Store(id="sidebar-state", data={"open": False}),
      dcc.Location(id="url"),
      sidebar,
      html.Div(
        [
          content
          ],
        # id="page-content"
      )]
    )
  ],
      fluid=True,
      className="py-1",)