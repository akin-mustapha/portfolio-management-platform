"""Atom — single-element badge components."""

from dash import html


def _kpi_badge(label, value_str, unit="", change_sign=0):
    change_class = (
        "kpi-change-positive"
        if change_sign > 0
        else "kpi-change-negative" if change_sign < 0 else "kpi-change-neutral"
    )
    return html.Div(
        [
            html.Span(label, className="kpi-badge__label"),
            html.Div(
                [
                    html.Span(value_str, className=f"kpi-badge__value {change_class}"),
                    html.Span(unit, className="kpi-badge__unit") if unit else None,
                ],
                className="d-flex align-items-baseline gap-1",
            ),
        ],
        className="kpi-badge",
    )


def _tag_badge(value_str, accent=None):
    style = {"borderColor": accent, "color": accent} if accent else {}
    return html.Div(
        html.Span(value_str, className="tag-badge__value"),
        className="tag-badge",
        style=style,
    )
