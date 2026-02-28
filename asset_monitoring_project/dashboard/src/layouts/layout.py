import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, callback
from dashboard.src.pages.portfolio.portfolio_page import portfolio_layout
from dashboard.src.pages.asset.asset_page import asset_layout
from dashboard.src.pages.tag.tag_page import tag_layout
from dashboard.src.layouts.horizontal_sidebar import horizontal_sidebar
from services.portfolio.portfolio_service_builder import build_portfolio_service

from dashboard.src.components.buttons import btn_side_toggle

porfoltio_serivce = build_portfolio_service()

@callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
  if pathname == "/portfolio":
    return portfolio_layout()
  elif pathname == "/assets":
    return asset_layout()
  elif pathname == "/tag":
    return tag_layout()
  # If the user tries to reach a different page, return a 404 message
  return html.Div(
    [
      html.H1("404: Not found", className="text-danger"),
      html.Hr(),
      html.P(f"The pathname {pathname} was not recognised..."),
    ],
    className="p-3 bg-light rounded-3",
  )

from dash import callback, Input, Output, State, no_update
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
        dbc.Row(
            dbc.Col(
                horizontal_sidebar,
                width=12,
                lg=12,
                # className="px-0"
            ),
            className="mb-2"
        ),
        dbc.Row(
            dbc.Col(
                dcc.Loading(
                    type="circle",
                    children=dbc.Card(
                        dbc.CardBody(html.Div(id="page-content")),
                        className="shadow-sm border-0"
                    )
                ),
                width=12,
                lg=12,
                # className="mx-auto"
                className="mx-auto px-2 px-md-4"
            )
        ),
    ],
    fluid=True,
    className="py-2",
)