"""Organism — primary KPI row (full portfolio summary header)."""
import dash_bootstrap_components as dbc
from dash import html

from ..atoms.formatters import _fmt_currency, _fmt_pct, _pnl_pct
from ..molecules.kpi_card import _dark_kpi_card


def kpi_row(data=None):
    data = data or {}
    currency = data.get("currency", "#")
    unit = "EUR" if currency == "EUR" else "USD"
    currency_sign = "€" if currency == "EUR" else "$"

    value = data.get("value", 0)
    total_invested = data.get("total_cost", 0)
    unrealized_pnl = data.get("unrealized_pnl", 0)
    realized_pnl = data.get("realized_pnl", 0)
    cash = data.get("cash", 0)
    cash_pct = (cash / value * 100) if value else 0
    cash_is_zero = not cash
    cash_reserved = data.get("cash_reserved", 0)
    cash_in_pies = data.get("cash_in_pies", 0)
    cash_reserved_pct = (cash_reserved / value * 100) if value else 0
    cash_in_pies_pct = (cash_in_pies / value * 100) if value else 0

    unrealized_pct = _pnl_pct(unrealized_pnl, total_invested)
    realized_pct = _pnl_pct(realized_pnl, total_invested)

    return html.Div([
        # Group labels — desktop only
        dbc.Row([
            dbc.Col(html.Span("Performance", className="kpi-group-label"), xs=6, md=True),
            dbc.Col(xs=6, md=True),
            dbc.Col(xs=6, md=True),
            dbc.Col(xs=6, md=True),
            dbc.Col(html.Span("Cash", className="kpi-group-label"), xs=6, md=True),
            dbc.Col(xs=6, md=True),
            dbc.Col(xs=6, md=True),
        ], className="mb-1 d-none d-md-flex g-3"),

        dbc.Row([
            dbc.Col(_dark_kpi_card(
                "Portfolio Value",
                _fmt_currency(value, currency_sign),
                unit=unit,
            ), xs=6, md=True),
            dbc.Col(_dark_kpi_card(
                "Total Invested",
                _fmt_currency(total_invested, currency_sign),
                unit=unit,
            ), xs=6, md=True),
            dbc.Col(_dark_kpi_card(
                "Unrealized P&L",
                _fmt_currency(unrealized_pnl, currency_sign),
                unit=unit,
                change_str=_fmt_pct(unrealized_pct) if unrealized_pct is not None else "",
                change_sign=1 if unrealized_pnl > 0 else (-1 if unrealized_pnl < 0 else 0),
            ), xs=6, md=True),
            dbc.Col(_dark_kpi_card(
                "Realized P&L",
                _fmt_currency(realized_pnl, currency_sign),
                unit=unit,
                change_str=_fmt_pct(realized_pct) if realized_pct is not None else "",
                change_sign=1 if realized_pnl > 0 else (-1 if realized_pnl < 0 else 0),
            ), xs=6, md=True),
            dbc.Col(_dark_kpi_card(
                "Cash Available",
                _fmt_currency(cash, currency_sign),
                unit=unit,
                change_str=_fmt_pct(cash_pct),
                change_sign=0,
                extra_class="kpi-card-zero" if cash_is_zero else "",
            ), xs=6, md=True),
            dbc.Col(_dark_kpi_card(
                "Cash Reserved",
                _fmt_currency(cash_reserved, currency_sign),
                unit=unit,
                change_str=_fmt_pct(cash_reserved_pct),
                change_sign=0,
            ), xs=6, md=True),
            dbc.Col(_dark_kpi_card(
                "Cash in Pies",
                _fmt_currency(cash_in_pies, currency_sign),
                unit=unit,
                change_str=_fmt_pct(cash_in_pies_pct),
                change_sign=0,
            ), xs=6, md=True),
        ], className="g-3"),
    ], className="mb-4")
