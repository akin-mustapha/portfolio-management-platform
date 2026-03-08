from dash import Dash
import dash_bootstrap_components as dbc
from dashboard.src.layouts.layout import layout


plotly_config = {
  "staticPlot": True,
#   "scrollZoom": True,
  "displayModeBar": False,
  "editable": True,
}


# App
app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.COSMO, dbc.icons.FONT_AWESOME]
    )

app.layout = layout


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=8050,
        debug=True
    )