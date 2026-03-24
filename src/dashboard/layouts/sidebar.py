
from dash import html
import dash_bootstrap_components as dbc
from ..components.atoms.buttons import privacy_toggle_btn


def _nav_item(icon_class, label, href):
    return dbc.NavLink(
        href=href,
        active="exact",
        className="sidebar-nav-item d-flex align-items-center gap-2 px-3 py-2 rounded-2 text-decoration-none",
        children=[
            html.I(className=f"{icon_class} sidebar-nav-icon"),
            html.Span(label, className="sidebar-nav-label"),
        ],
    )


vertical_sidebar = html.Div(
    [
        # Brand header
        html.Div(
            [
                html.Div(
                    html.I(className="fa-solid fa-gauge-high text-white", style={"fontSize": "0.9rem"}),
                    style={
                        "width": "30px",
                        "height": "30px",
                        "borderRadius": "8px",
                        "background": "linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%)",
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "flexShrink": "0",
                    }
                ),
                html.Div([
                    html.Span("Asset", className="sidebar-brand-title fw-bold"),
                    html.Br(),
                    html.Span("Monitor", className="sidebar-brand-subtitle"),
                ]),
            ],
            className="d-flex align-items-center gap-2 px-3 py-3",
        ),

        html.Div(className="sidebar-divider"),

        # Navigation section label
        html.Div("MENU", className="sidebar-menu-label"),

        # Nav links
        dbc.Nav(
            [
                _nav_item("fa-solid fa-chart-pie", "Portfolio", "/portfolio"),
                _nav_item("fa-solid fa-coins", "Assets", "/assets"),
                _nav_item("fa-solid fa-tag", "Tags", "/tag"),
            ],
            vertical=True,
            pills=False,
            className="px-2 flex-grow-1",
        ),

        # Bottom utility icons
        html.Div(className="sidebar-divider sidebar-divider--bottom"),
        html.Div(
            [
                html.Div(
                    html.I(className="fa-solid fa-circle-question sidebar-help-icon"),
                    className="px-3 py-2",
                ),
                privacy_toggle_btn(),
                html.Div(
                    html.Button(
                        html.I(id="theme-toggle-icon", className="fa-solid fa-moon"),
                        id="theme-toggle-btn",
                        n_clicks=0,
                        className="theme-toggle-btn",
                        title="Toggle dark/light mode",
                    ),
                    className="px-3 py-2",
                ),
            ],
            className="d-flex align-items-center",
        ),
    ],
    id="sidebar",
    className="d-flex flex-column",
    style={
        "width": "190px",
        "height": "100vh",
        "position": "sticky",
        "top": "0",
        "overflowY": "auto",
        "paddingBottom": "1rem",
        "flexShrink": "0",
    },
)
