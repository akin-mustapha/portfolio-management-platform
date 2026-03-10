import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, callback, State
from ..pages.portfolio.portfolio_page import portfolio_layout
from ..pages.asset.asset_page import asset_layout
from ..pages.tag.tag_page import tag_layout
from ..layouts.sidebar import vertical_sidebar
from src.services.portfolio.portfolio_service_builder import build_portfolio_service
from ..pages.portfolio import theme_callbacks  # noqa: F401

porfoltio_serivce = build_portfolio_service()

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

    porfoltio_serivce.create_tag(value)
    return f"Tag '{value}' created"

# Layout
layout = dbc.Container(
    [
        dcc.Location(id="url"),
        dcc.Store(id="active-page"),
        dcc.Store(id="theme-store", storage_type="local", data="light"),
        dbc.Row(
            [
                dbc.Col(vertical_sidebar, width="auto", className="px-0"),
                dbc.Col(
                    dcc.Loading(
                        type="circle",
                        children=dbc.Card(
                            dbc.CardBody(html.Div(id="page-content")),
                            className="shadow-sm border-0"
                        )
                    ),
                    className="px-3 py-3"
                ),
            ],
            className="g-0",
            style={"minHeight": "100vh"}
        ),
    ],
    fluid=True,
    className="py-0 px-0",
)
