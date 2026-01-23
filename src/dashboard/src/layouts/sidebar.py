
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, callback
from src.dashboard.src.layouts.portfolio import portfolio_layout
from src.dashboard.src.services.portfolio_service import PortfolioService



# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
  "position": "fixed",
  "top": 0,
  "left": 0,
  "bottom": 0,
  "width": "16rem",
  "padding": "2rem 1rem",
  # "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
  "margin-left": "18rem",
  "margin-right": "2rem",
  "padding": "2rem 1rem",
}

sidebar = html.Div(
  [
    html.H2("Sidebar", className="display-7"),
    html.Hr(),
    dbc.Nav(
      [
        dbc.NavLink("Home", href="/", active="exact"),
        dbc.NavLink("Portfolio", href="/portfolio", active="exact"),
        dbc.NavLink("Asset", href="/asset", active="exact"),
      ],
      vertical=True,
      pills=True,
    ),
  ],
  style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)