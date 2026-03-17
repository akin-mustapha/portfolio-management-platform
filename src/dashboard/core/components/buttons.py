import dash_bootstrap_components as dbc
from dash import html

# toggle button outside sidebar
btn_side_toggle = dbc.Button("☰", id="sidebar-toggle",color="primary",
                        style={"position": "fixed", "top": "1rem", "left": "1rem", "zIndex": 999})


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
