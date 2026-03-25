"""Asset Profile tab — KPI strip, asset summary, and drag-to-plot chart zone."""

import dash_bootstrap_components as dbc
from dash import dcc, html


def _summary_prop(label, value_id):
    return html.Div(
        [
            html.Div(label, className="prop-label"),
            html.Div("—", id=value_id, className="prop-value"),
        ],
        className="profile-summary-prop",
    )


def _summary_badge(label, value_id):
    """Like _summary_prop but renders as a kpi-badge pill."""
    return html.Div(
        [
            html.Span(label, className="kpi-badge__label"),
            html.Span("—", id=value_id, className="kpi-badge__value"),
        ],
        className="kpi-badge",
    )


def _empty_state():
    return html.Div(
        "Select an asset from the table to begin.",
        className="tv-placeholder-text",
        style={"padding": "24px 0", "color": "var(--text-muted)", "fontSize": "0.85rem"},
    )


def asset_profile_tab_content():
    return html.Div(
        [
            # ── Position snapshot strip (badges are draggable) ─────────
            html.Div(id="profile-snapshot-strip", className="mb-3"),
            # ── Asset metadata card ────────────────────────────────────
            html.Div(
                [
                    html.Div("Asset Details", className="tv-section-header"),
                    # Row 1: identity
                    dbc.Row(
                        [
                            dbc.Col(_summary_prop("Ticker", "profile-ticker"), width=2),
                            dbc.Col(_summary_prop("Name", "profile-name"), width=3),
                            dbc.Col(
                                _summary_prop("Description", "profile-description"),
                                width=4,
                            ),
                            dbc.Col(
                                _summary_prop("First Seen", "profile-created"), width=2
                            ),
                            dbc.Col(
                                _summary_prop(
                                    "Last Ingestion", "profile-last-ingestion"
                                ),
                                width=1,
                            ),
                        ],
                        className="g-3 mb-3",
                    ),
                    html.Hr(className="tv-divider"),
                    # Row 2: classification — sector/industry as badges
                    dbc.Row(
                        [
                            dbc.Col(
                                _summary_prop("Tags", "profile-summary-tags"), width=3
                            ),
                            dbc.Col(
                                _summary_prop("Category", "profile-summary-category"),
                                width=3,
                            ),
                            dbc.Col(
                                html.Div(
                                    [_summary_badge("Industry", "profile-summary-industry")],
                                    className="kpi-badge-row",
                                ),
                                width=3,
                            ),
                            dbc.Col(
                                html.Div(
                                    [_summary_badge("Sector", "profile-summary-sector")],
                                    className="kpi-badge-row",
                                ),
                                width=3,
                            ),
                        ],
                        className="g-3",
                    ),
                ],
                className="tv-section-container mb-3",
            ),
            # ── Hidden drag-drop bridge (no visible card) ──────────────
            html.Button(id="_drop-btn", n_clicks=0, style={"display": "none"}),
            dcc.Store(id="drop-metric-store", data=""),
            # ── Asset detail cards — populated on row selection ────────
            html.Div(id="asset-detail-sections", children=_empty_state()),
        ],
        className="workspace-wrapper",
        id="tab-tags-content",
    )
