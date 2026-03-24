"""Molecule — KPI card components (atoms combined with a single job)."""
from dash import dcc, html

from ..atoms.formatters import _fmt_pct
from ...charts.sparklines import daily_change_sparkline


def _daily_change_card(daily_change_pct, daily_change_series, theme="light"):
    change_sign = (
        1 if (daily_change_pct or 0) > 0 else
        -1 if (daily_change_pct or 0) < 0 else
        0
    )
    change_class = (
        "kpi-change-positive" if change_sign > 0 else
        "kpi-change-negative" if change_sign < 0 else
        "kpi-change-neutral"
    )
    value_str = _fmt_pct(daily_change_pct) if daily_change_pct is not None else "—"
    has_series = daily_change_series is not None and daily_change_series.get("dates")
    spark = html.Div(
        dcc.Graph(
            figure=daily_change_sparkline(daily_change_series, change_sign, theme),
            config={"displayModeBar": False, "staticPlot": True},
            responsive=False,
            style={"height": "22px", "width": "56px", "display": "block"},
        ),
        style={"width": "56px", "height": "22px", "overflow": "hidden", "flex": "0 0 56px", "lineHeight": 0},
    ) if has_series else None
    return html.Div([
        html.Span("Daily Change", className="kpi-badge__label"),
        html.Div([
            html.Span(value_str, className=f"kpi-badge__value {change_class}"),
            spark,
        ], className="d-flex align-items-center gap-2"),
    ], className="kpi-badge kpi-badge--with-spark")


def _dark_kpi_card(label, value_str, unit="", change_str="", change_sign=0, extra_class=""):
    change_class = (
        "kpi-change-positive" if change_sign > 0 else
        "kpi-change-negative" if change_sign < 0 else
        "kpi-change-neutral"
    )
    card_class = f"kpi-card {extra_class}".strip()
    return html.Div([
        html.Div(label, className="kpi-label"),
        html.Div([
            html.Div([
                html.Span(value_str, className="kpi-value"),
                html.Span(unit, className="kpi-unit") if unit else None,
            ], className="d-flex align-items-baseline"),
            html.Span(change_str, className=f"kpi-change {change_class}") if change_str else None,
        ], className="d-flex align-items-baseline justify-content-between"),
    ], className=card_class)
