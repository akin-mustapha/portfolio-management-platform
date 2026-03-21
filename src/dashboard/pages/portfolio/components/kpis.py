import dash_bootstrap_components as dbc
from dash import html


def _fmt_currency(value, sign):
    return f"{sign}{value:,.2f}"


def _fmt_pct(value):
    prefix = "+" if value > 0 else ""
    return f"{prefix}{value:.2f}%"


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


def _pnl_pct(pnl, total_invested):
    """Return % return relative to total invested, or None if indeterminate."""
    if total_invested and total_invested != 0:
        return (pnl / total_invested) * 100
    return None


def kpi_row(data=None):
    data = data or {}
    currency = data.get("currency", "#")
    unit = "EUR" if currency == "EUR" else "USD"
    currency_sign = "€" if currency == "EUR" else "$"

    value = data.get("value", 0)
    total_invested = data.get("total_cost", 0)
    realized_pnl = data.get("realized_pnl", 0)
    unrealized_pnl = data.get("unrealized_pnl", 0)
    cash = data.get("cash", 0)
    cash_pct = (cash / value * 100) if value else 0
    cash_is_zero = not cash
    cash_reserved = data.get("cash_reserved", 0)
    cash_in_pies = data.get("cash_in_pies", 0)
    cash_reserved_pct = (cash_reserved / value * 100) if value else 0
    cash_in_pies_pct = (cash_in_pies / value * 100) if value else 0
    daily_change_pct = data.get("daily_change_pct")
    portfolio_vol = data.get("portfolio_vol")

    unrealized_pct = _pnl_pct(unrealized_pnl, total_invested)
    realized_pct = _pnl_pct(realized_pnl, total_invested)

    return html.Div([
        # Group labels — desktop only
        dbc.Row([
            dbc.Col(html.Span("Performance", className="kpi-group-label"), xs=6, md=True),
            dbc.Col(xs=6, md=True),
            dbc.Col(xs=6, md=True),
            dbc.Col(xs=6, md=True),
            dbc.Col(xs=6, md=True),
            dbc.Col(html.Span("Risk", className="kpi-group-label"), xs=6, md=True),
            dbc.Col(html.Span("Cash", className="kpi-group-label"), xs=6, md=True),
            dbc.Col(xs=6, md=True),
            dbc.Col(xs=6, md=True),
        ], className="mb-1 d-none d-md-flex g-3"),

        # KPI cards
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
                "Daily Change",
                _fmt_pct(daily_change_pct) if daily_change_pct is not None else "—",
                change_sign=1 if (daily_change_pct or 0) > 0 else (-1 if (daily_change_pct or 0) < 0 else 0),
            ), xs=6, md=True),
            dbc.Col(_dark_kpi_card(
                "Volatility 30D",
                f"{portfolio_vol:.4f}" if portfolio_vol is not None else "—",
                unit="weighted",
                change_sign=0,
            ), xs=6, md=True, className="kpi-group-separator-col"),
            dbc.Col(_dark_kpi_card(
                "Cash Available",
                _fmt_currency(cash, currency_sign),
                unit=unit,
                change_str=_fmt_pct(cash_pct),
                change_sign=0,
                extra_class="kpi-card-zero" if cash_is_zero else "",
            ), xs=6, md=True, className="kpi-group-separator-col"),
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
