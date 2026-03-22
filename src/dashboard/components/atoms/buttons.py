"""
Reusable button atoms — used in the top navbar and any page that needs them.
Add new shared buttons here (not in page-level components).
"""
import dash_bootstrap_components as dbc
from dash import html


def privacy_toggle_btn():
    return html.Div(
        html.Button(
            html.I(id="privacy-toggle-icon", className="fa-solid fa-eye"),
            id="privacy-toggle-btn",
            n_clicks=0,
            className="theme-toggle-btn",
            title="Toggle privacy mode",
        ),
        className="px-3 py-2",
    )
