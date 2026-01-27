from dash import Dash
import dash_bootstrap_components as dbc
from src.dashboard.src.layouts.layout import layout


# App
app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.LUMEN, dbc.icons.FONT_AWESOME]
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