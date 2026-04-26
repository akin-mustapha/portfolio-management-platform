from dash import html
import dash_bootstrap_components as dbc

horizontal_sidebar = html.Div(
    [
        dbc.Nav(
            [
                html.Span("Asset Monitor", className="navbar-brand fw-semibold me-4"),
                dbc.NavLink("Portfolio", href="/portfolio", active="exact"),
                dbc.NavLink("Assets", href="/assets", active="exact"),
                dbc.NavLink("Tag", href="/tag", active="exact"),
            ],
            vertical=False,
            pills=True,
            className="mt-3 align-items-center",
        )
    ],
    id="sidebar",
)

content = html.Div(id="page-content")
