from dash import dcc, html, callback, Input, Output, State, dash
import dash_bootstrap_components as dbc
from ...components.cards import card
from src.services.portfolio.portfolio_service_builder import build_portfolio_service
# from src.dashboard.services.asset_service import AssetService
from ...controllers.local_asset_service import LocalAssetService
from ...styles.style import TAB_CONTENT_STYLE
from ...components.tables.table import create_table
from ...components.select import create_select
import pandas as pd


def tag_layout():
  return html.Div(
    [
       
      dcc.Location(id="tag_page_location"),
      dbc.Row(
        [
          html.p('empty')
          ],
          className="mt-4"
      ),
    ]
  )
