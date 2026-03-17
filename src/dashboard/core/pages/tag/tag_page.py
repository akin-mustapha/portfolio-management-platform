from dash import dcc, html
import dash_bootstrap_components as dbc


def tag_layout():
  return html.Div(
    [

      dcc.Location(id="tag_page_location"),
      dbc.Row(
        [
          html.P('empty')
          ],
          className="mt-4"
      ),
    ]
  )
