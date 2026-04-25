"""Asset Profile tab — drag-to-plot chart zone (unified per-asset cards)."""

from dash import dcc, html


def _empty_state():
    return html.Div(
        "Select an asset from the table to begin.",
        className="tv-placeholder-text",
        style={
            "padding": "24px 0",
            "color": "var(--text-muted)",
            "fontSize": "0.85rem",
        },
    )


def asset_profile_tab_content():
    return html.Div(
        [
            # Hidden drag-drop bridge
            html.Button(id="_drop-btn", n_clicks=0, style={"display": "none"}),
            dcc.Store(id="drop-metric-store", data=""),
            # Per-asset unified cards — populated on row selection
            html.Div(id="asset-detail-sections", children=_empty_state()),
        ],
        className="workspace-wrapper",
        id="tab-tags-content",
    )
