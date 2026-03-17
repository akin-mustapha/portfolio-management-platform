import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, callback, State
from ..pages.portfolio.portfolio_page import portfolio_layout
from ..pages.asset.asset_page import asset_layout
from ..pages.tag.tag_page import tag_layout
from backend.services.portfolio.portfolio_service_builder import build_portfolio_service
from ..pages.portfolio import theme_callbacks  # noqa: F401
from ..components.buttons import privacy_toggle_btn


def _top_navbar():
    return html.Div(
        [
            # Brand
            html.Div(
                [
                    html.Div(
                        html.I(className="fa-solid fa-gauge-high text-white", style={"fontSize": "0.85rem"}),
                        style={
                            "width": "28px",
                            "height": "28px",
                            "borderRadius": "7px",
                            "background": "linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%)",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "flexShrink": "0",
                        },
                    ),
                    html.Span("Asset Monitor", className="top-nav-brand"),
                ],
                className="d-flex align-items-center gap-2",
            ),
            # Nav links
            dbc.Nav(
                [
                    dbc.NavLink("Portfolio", href="/portfolio", active="exact", className="top-nav-link"),
                    dbc.NavLink("Assets", href="/assets", active="exact", className="top-nav-link"),
                    dbc.NavLink("Tags", href="/tag", active="exact", className="top-nav-link"),
                ],
                className="d-flex flex-row gap-1 ms-4",
            ),
            # Utility buttons — pushed to far right; always in DOM so theme callbacks work
            html.Div(
                [
                    html.Div(
                        html.I(className="fa-solid fa-circle-question", style={"fontSize": "1rem"}),
                        className="top-util-btn",
                        title="Help",
                    ),
                    privacy_toggle_btn(),
                    html.Div(
                        html.Button(
                            html.I(id="theme-toggle-icon", className="fa-solid fa-moon"),
                            id="theme-toggle-btn",
                            n_clicks=0,
                            className="theme-toggle-btn",
                            title="Toggle dark/light mode",
                        ),
                        className="px-2",
                    ),
                ],
                className="d-flex align-items-center ms-auto gap-1",
            ),
        ],
        id="top-navbar",
        className="top-navbar",
    )

portfolio_service = build_portfolio_service()

@callback(Output("page-content", "children"), Output("active-page", "data"), [Input("url", "pathname")])
def render_page_content(pathname):
  if pathname == "/portfolio":
    return portfolio_layout(), pathname
  elif pathname == "/assets":
    return asset_layout(), pathname
  elif pathname == "/tag":
    return tag_layout(), pathname
  # If the user tries to reach a different page, return a 404 message
  return html.Div(
    [
      html.H1("404: Not found", className="text-danger"),
      html.Hr(),
      html.P(f"The pathname {pathname} was not recognised..."),
    ],
    className="p-3 bg-light rounded-3",
  ), pathname

@callback(
    Output("tag-create-status", "value"),
    Input("btn-create-tag-name", "n_clicks"),
    State("input-tag-name", "value"),
    prevent_initial_call=True
)
def create_new_tag(n_clicks, value):
    if not value:
        return "Tag name cannot be empty"

    portfolio_service.create_tag(value)
    return f"Tag '{value}' created"

# Layout
layout = dbc.Container(
    [
        dcc.Location(id="url"),
        dcc.Store(id="active-page"),
        dcc.Store(id="theme-store", storage_type="local", data="light"),
        dcc.Store(id="privacy-store", storage_type="local", data=False),
        _top_navbar(),
        dbc.Card(
            dbc.CardBody(html.Div(id="page-content")),
            className="shadow-sm border-0 rounded-0"
        ),
    ],
    fluid=True,
    className="py-0 px-0",
)
