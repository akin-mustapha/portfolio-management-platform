"""Shared helpers used across all tab content builders."""
from dash import html

_GRAPH_CONFIG = {"displayModeBar": False}


def _chart_section(title, chart):
    return html.Div([
        html.Div(title, className="tv-section-header"),
        chart,
    ])


def _loading_placeholder(tab_id, message="Loading…"):
    return html.Div(
        html.P(message, className="text-muted text-center py-5"),
        id=tab_id,
    )
