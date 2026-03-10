
from dash import html
import dash_bootstrap_components as dbc


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
                    html.Span("Asset", className="fw-bold", style={"fontSize": "0.85rem", "color": "#1a1a2e", "lineHeight": "1.1"}),
                    html.Br(),
                    html.Span("Monitor", style={"fontSize": "0.75rem", "color": "#6c757d", "lineHeight": "1.1"}),
                ]),
            ],
            className="d-flex align-items-center gap-2 px-3 py-3",
        ),

        html.Div(style={"height": "1px", "background": "#e9ecef", "margin": "0 12px 8px"}),

        # Navigation section label
        html.Div("MENU", style={
            "fontSize": "0.65rem",
            "fontWeight": "700",
            "letterSpacing": "0.08em",
            "color": "#adb5bd",
            "padding": "0 12px 6px",
        }),

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
        html.Div(style={"height": "1px", "background": "#e9ecef", "margin": "8px 12px"}),
        html.Div(
            [
                html.Div(
                    html.I(className="fa-solid fa-circle-question", style={"color": "#adb5bd", "fontSize": "1rem"}),
                    className="px-3 py-2",
                ),
            ],
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
        "background": "#f8f9fa",
        "boxShadow": "1px 0 0 #e9ecef",
        "paddingBottom": "1rem",
        "flexShrink": "0",
    },
)
