from dash import Dash
import dash_bootstrap_components as dbc
from src.dashboard.src.layouts.layout import layout

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

# Set ploting default
# pio.templates.default = "plotly_dark"
# px.defaults.height = 600
# px.defaults.template = "plotly_dark"
# px.defaults.color_continuous_scale = px.colors.sequential.Bluyl_r
# px.defaults.color_discrete_sequence = px.colors.sequential.Bluyl_r


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
    # app.run(
    #     debug=True)
    app.run(
        host='0.0.0.0',
        port=8050,
        debug=True
    )