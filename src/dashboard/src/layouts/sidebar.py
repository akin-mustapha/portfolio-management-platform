
from dash import html
import dash_bootstrap_components as dbc


vertical_sidebar = html.Div([
    html.H5("Asset Monitor", className="fw-semibold px-3 pt-3 pb-2"),
    html.Hr(className="my-0"),
    dbc.Nav(
        [
            dbc.NavLink("Portfolio", href="/portfolio", active="exact"),
            dbc.NavLink("Assets", href="/assets", active="exact"),
            dbc.NavLink("Tag", href="/tag", active="exact"),
        ],
        vertical=True,
        pills=True,
        className="mt-2"
    )
], id="sidebar", style={
    "width": "200px",
    "minHeight": "100vh",
    "borderRight": "1px solid #dee2e6",
    "paddingTop": "0.5rem"
})
