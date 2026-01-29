
import dash
from dash import Input, Output, dcc, html, callback, State
import dash_bootstrap_components as dbc

horizontal_sidebar = html.Div([
    dbc.Nav(
        [
            dbc.NavLink("Portfolio", href="/portfolio", active="exact"),
            dbc.NavLink("Assets", href="/assets", active="exact"),
            dbc.NavLink("Tag", href="/tag", active="exact"),
        ],
        vertical=False,
        pills=True,
        className="mt-3"
    )
], id="sidebar")

content = html.Div(id="page-content")