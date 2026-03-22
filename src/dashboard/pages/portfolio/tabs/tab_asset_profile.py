"""Asset Profile tab — read-only summary card with ticker metadata and tags."""
import dash_bootstrap_components as dbc
from dash import html


def _summary_prop(label, value_id):
    return html.Div([
        html.Div(label, className="prop-label"),
        html.Div("—", id=value_id, className="prop-value"),
    ], className="profile-summary-prop")


def asset_profile_tab_content():
    return html.Div([

        # ── Read-only summary card ─────────────────────────────────
        html.Div([
            html.Div("Asset Details", className="summary-card-header"),

            # Row 1: identity
            dbc.Row([
                dbc.Col(_summary_prop("Ticker",          "profile-ticker"),          width=2),
                dbc.Col(_summary_prop("Name",            "profile-name"),            width=3),
                dbc.Col(_summary_prop("Description",     "profile-description"),     width=4),
                dbc.Col(_summary_prop("First Seen",      "profile-created"),         width=2),
                dbc.Col(_summary_prop("Last Ingestion",  "profile-last-ingestion"),  width=1),
            ], className="g-3 mb-3"),

            html.Hr(className="tv-divider"),

            # Row 2: classification
            dbc.Row([
                dbc.Col(_summary_prop("Tags",      "profile-summary-tags"),      width=3),
                dbc.Col(_summary_prop("Category",  "profile-summary-category"),  width=3),
                dbc.Col(_summary_prop("Industry",  "profile-summary-industry"),  width=3),
                dbc.Col(_summary_prop("Sector",    "profile-summary-sector"),    width=3),
            ], className="g-3"),

        ], className="profile-summary-card mb-4"),

    ], id="tab-tags-content")
