"""Asset Profile tab — position snapshot, price/MA chart, and metadata card."""
import dash_bootstrap_components as dbc
from dash import dcc, html


def _summary_prop(label, value_id):
    return html.Div([
        html.Div(label, className="prop-label"),
        html.Div("—", id=value_id, className="prop-value"),
    ], className="profile-summary-prop")


def asset_profile_tab_content():
    return html.Div([

        # ── Position snapshot strip ────────────────────────────────
        html.Div(id="profile-snapshot-strip", className="mb-3"),

        # ── Price + MA chart ───────────────────────────────────────
        dcc.Graph(
            id="profile-price-ma-chart",
            config={"displayModeBar": False},
            style={"height": "220px"},
            className="mb-4",
        ),

        # ── Asset metadata card ────────────────────────────────────
        html.Div([
            html.Div("Asset Details", className="tv-section-header"),

            # Row 1: identity
            dbc.Row([
                dbc.Col(_summary_prop("Ticker",         "profile-ticker"),         width=2),
                dbc.Col(_summary_prop("Name",           "profile-name"),           width=3),
                dbc.Col(_summary_prop("Description",    "profile-description"),    width=4),
                dbc.Col(_summary_prop("First Seen",     "profile-created"),        width=2),
                dbc.Col(_summary_prop("Last Ingestion", "profile-last-ingestion"), width=1),
            ], className="g-3 mb-3"),

            html.Hr(className="tv-divider"),

            # Row 2: classification
            dbc.Row([
                dbc.Col(_summary_prop("Tags",     "profile-summary-tags"),     width=3),
                dbc.Col(_summary_prop("Category", "profile-summary-category"), width=3),
                dbc.Col(_summary_prop("Industry", "profile-summary-industry"), width=3),
                dbc.Col(_summary_prop("Sector",   "profile-summary-sector"),   width=3),
            ], className="g-3"),

        ], className="tv-section-container"),

    ], className="workspace-wrapper", id="tab-tags-content")
