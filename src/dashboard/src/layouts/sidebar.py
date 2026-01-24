
import dash
from dash import Input, Output, dcc, html, callback, State
import dash_bootstrap_components as dbc
from src.dashboard.src.services.portfolio_service import PortfolioService

from src.dashboard.src.styles.style import SIDEBAR_HIDDEN, SIDEBAR_STYLE, CONTENT_STYLE, CONTENT_STYLE_EXPANDED

sidebar = dbc.Container([
    dbc.Nav(
        [
            dbc.NavLink("Portfolio", href="/portfolio", active="exact"),
            dbc.NavLink("Asset", href="/asset", active="exact"),
        ],
        vertical=True,
        pills=True,
        # className="mt-5"
    )
], id="sidebar", style=SIDEBAR_STYLE)

content = html.Div(id="page-content", style=CONTENT_STYLE)

@callback(
    Output("sidebar", "style"),
    Output("page-content", "style"),
    Output("sidebar-state", "data"),
    Input("sidebar-toggle", "n_clicks"),
    State("sidebar-state", "data"),
    prevent_initial_call=True
)
def toggle_sidebar(n_clicks, state):
    is_open = state["open"]
    # toggle
    new_open = not is_open
    
    if new_open:
        sidebar_style = SIDEBAR_STYLE
        content_style = CONTENT_STYLE
    else:
        sidebar_style = SIDEBAR_HIDDEN
        content_style = CONTENT_STYLE_EXPANDED
        
    return sidebar_style, content_style, {"open": new_open}