from dash import Dash
import dash_bootstrap_components as dbc
from src.dashboard.src.layouts.layout import layout


# App
app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.DARKLY, dbc.icons.FONT_AWESOME]
    )

app.layout = layout


if __name__ == "__main__":
    app.run(debug=True)