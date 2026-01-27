
import dash
from dash import Input, Output, dcc, html, callback, State
import dash_bootstrap_components as dbc
from src.dashboard.src.layouts.portfolio import portfolio_layout
from src.dashboard.src.services.portfolio_service import PortfolioService



# sidebar + content styles
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "4rem 1rem 1rem 1rem",
    "transition": "all 0.3s",
    # "overflow": "hidden",
}

SIDEBAR_HIDDEN = SIDEBAR_STYLE.copy()
SIDEBAR_HIDDEN["width"] = "0rem"
SIDEBAR_HIDDEN["padding"] = "4rem 0 0 0"
SIDEBAR_HIDDEN["visibility"] = "hidden"

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
    "transition": "margin-left 0.3s",
}

CONTENT_STYLE_EXPANDED = CONTENT_STYLE.copy()
CONTENT_STYLE_EXPANDED["margin-left"] = "0rem"

sidebar = html.Div([
    dbc.Nav(
        [
            dbc.NavLink("Portfolio", href="/portfolio", active="exact"),
            dbc.NavLink("Asset", href="/asset", active="exact"),
            dbc.NavLink("Tag", href="/tag", active="exact"),
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