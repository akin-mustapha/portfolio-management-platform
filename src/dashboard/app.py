from dash import Dash
import dash_bootstrap_components as dbc
from src.dashboard.src.layouts.layout import layout


# App
app = Dash(external_stylesheets=[dbc.themes.DARKLY])

app.layout = layout


if __name__ == "__main__":
    app.run(debug=True)