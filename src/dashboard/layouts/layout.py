import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, callback
from ..pages.portfolio.portfolio_page import portfolio_layout
from ..pages.portfolio import callbacks  # noqa: F401
from ..components.atoms.buttons import privacy_toggle_btn


def _top_navbar():
    return html.Div(
        [
            # Brand
            html.Div(
                [
                    html.Div(
                        html.I(
                            className="fa-solid fa-gauge-high text-white",
                            style={"fontSize": "0.85rem"},
                        ),
                        style={
                            "width": "28px",
                            "height": "28px",
                            "borderRadius": "7px",
                            "background": "linear-gradient(135deg, #0d6efd 0%, #0a58ca 100%)",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "flexShrink": "0",
                        },
                    ),
                    html.Span("Asset Monitor", className="top-nav-brand"),
                ],
                className="d-flex align-items-center gap-2",
            ),
            # Nav links
            dbc.Nav(
                [
                    dbc.NavLink(
                        "Portfolio",
                        href="/portfolio",
                        active="exact",
                        className="top-nav-link",
                    ),
                ],
                className="d-flex flex-row gap-1 ms-4",
            ),
            # Utility buttons — pushed to far right; always in DOM so theme callbacks work
            html.Div(
                [
                    privacy_toggle_btn(),
                    html.Button(
                        html.I(className="fa-solid fa-gear"),
                        id="settings-btn",
                        n_clicks=0,
                        className="top-util-btn",
                        title="Settings",
                    ),
                    html.Div(
                        html.Button(
                            html.I(
                                id="theme-toggle-icon", className="fa-solid fa-moon"
                            ),
                            id="theme-toggle-btn",
                            n_clicks=0,
                            className="theme-toggle-btn",
                            title="Toggle dark/light mode",
                        ),
                        className="px-2",
                    ),
                ],
                className="d-flex align-items-center ms-auto gap-1",
            ),
        ],
        id="top-navbar",
        className="top-navbar",
    )


@callback(
    Output("page-content", "children"),
    Output("active-page", "data"),
    [Input("url", "pathname")],
)
def render_page_content(pathname):
    if pathname == "/portfolio":
        return portfolio_layout(), pathname
    # If the user tries to reach a different page, return a 404 message
    return (
        html.Div(
            [
                html.H1("404: Not found", className="text-danger"),
                html.Hr(),
                html.P(f"The pathname {pathname} was not recognised..."),
            ],
            className="p-3 bg-light rounded-3",
        ),
        pathname,
    )


# Layout
layout = dbc.Container(
    [
        dcc.Location(id="url"),
        dcc.Store(id="active-page"),
        dcc.Store(id="theme-store", storage_type="local", data="light"),
        dcc.Store(id="privacy-store", storage_type="local", data=False),
        dcc.Store(id="api-key-store", storage_type="local", data=""),
        dcc.Store(id="api-url-store", storage_type="local", data=""),
        _top_navbar(),
        dbc.Card(
            dbc.CardBody(html.Div(id="page-content")),
            className="shadow-sm border-0 rounded-0",
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Settings"), close_button=True),
                dbc.ModalBody(
                    dbc.Row(
                        [
                            # Left sidebar — col-3
                            dbc.Col(
                                [
                                    html.Div(
                                        "API Setup",
                                        className="settings-nav-item settings-nav-item--active",
                                    ),
                                ],
                                width=3,
                                className="settings-sidebar",
                            ),
                            # Right content — col-9
                            dbc.Col(
                                [
                                    html.P(
                                        "API Configuration",
                                        className="settings-section-label",
                                    ),
                                    # URL row
                                    html.Div(
                                        [
                                            html.Label(
                                                "Base URL",
                                                className="settings-field-label",
                                            ),
                                            dbc.Input(
                                                id="settings-api-url-input",
                                                type="url",
                                                placeholder="https://live.trading212.com",
                                                className="settings-api-input",
                                            ),
                                        ],
                                        className="settings-field-group",
                                    ),
                                    # Key row
                                    html.Div(
                                        [
                                            html.Label(
                                                "API Key",
                                                className="settings-field-label",
                                            ),
                                            html.Div(
                                                [
                                                    dbc.Input(
                                                        id="settings-api-key-input",
                                                        type="password",
                                                        placeholder="Enter Trading212 API key",
                                                        className="settings-api-input",
                                                    ),
                                                    html.Button(
                                                        html.I(
                                                            id="settings-key-eye-icon",
                                                            className="fa-solid fa-eye",
                                                        ),
                                                        id="settings-key-eye-btn",
                                                        n_clicks=0,
                                                        className="settings-eye-btn",
                                                        title="Show/hide key",
                                                    ),
                                                ],
                                                className="settings-input-row",
                                            ),
                                        ],
                                        className="settings-field-group",
                                    ),
                                    # Secret token row
                                    html.Div(
                                        [
                                            html.Label(
                                                "Secret Token",
                                                className="settings-field-label",
                                            ),
                                            html.Div(
                                                [
                                                    dbc.Input(
                                                        id="settings-secret-token-input",
                                                        type="password",
                                                        placeholder="Enter secret token",
                                                        className="settings-api-input",
                                                    ),
                                                    html.Button(
                                                        html.I(
                                                            id="settings-secret-eye-icon",
                                                            className="fa-solid fa-eye",
                                                        ),
                                                        id="settings-secret-eye-btn",
                                                        n_clicks=0,
                                                        className="settings-eye-btn",
                                                        title="Show/hide token",
                                                    ),
                                                ],
                                                className="settings-input-row",
                                            ),
                                        ],
                                        className="settings-field-group",
                                    ),
                                    # Action buttons
                                    html.Div(
                                        [
                                            html.Button(
                                                "Connect",
                                                id="settings-connect-btn",
                                                n_clicks=0,
                                                className="settings-connect-btn",
                                            ),
                                            html.Button(
                                                "Save",
                                                id="settings-save-btn",
                                                n_clicks=0,
                                                className="tv-apply-btn",
                                            ),
                                            html.Span(
                                                id="settings-save-status",
                                                className="settings-save-status",
                                            ),
                                        ],
                                        className="settings-actions-row",
                                    ),
                                    # Connection status
                                    html.Div(
                                        [
                                            html.Span(
                                                id="settings-status-dot",
                                                className="settings-status-dot settings-status-dot--disconnected",
                                            ),
                                            html.Span(
                                                id="settings-status-label",
                                                children="Disconnected",
                                                className="settings-status-label",
                                            ),
                                        ],
                                        className="settings-status-row",
                                    ),
                                    # Last ingestion run
                                    html.Div(
                                        [
                                            html.Span(
                                                "Last ingestion run",
                                                className="settings-meta-label",
                                            ),
                                            html.Span(
                                                id="settings-last-run",
                                                children="—",
                                                className="settings-meta-value",
                                            ),
                                        ],
                                        className="settings-meta-row",
                                    ),
                                ],
                                width=9,
                                className="settings-content",
                            ),
                        ],
                        className="g-0 h-100",
                    ),
                    className="settings-modal-body",
                ),
            ],
            id="settings-modal",
            is_open=False,
            size="md",
            centered=True,
            backdrop=True,
            className="settings-modal",
        ),
    ],
    fluid=True,
    className="py-0 px-0",
)
