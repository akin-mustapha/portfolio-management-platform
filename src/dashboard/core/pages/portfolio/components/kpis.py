import dash_bootstrap_components as dbc
from dash import html


def _fmt_currency(value, sign):
    return f"{sign}{value:,.2f}"


def _fmt_pct(value):
    prefix = "+" if value > 0 else ""
    return f"{prefix}{value:.2f}%"


def _dark_kpi_card(label, value_str, unit="", change_str="", change_sign=0):
    change_class = (
        "kpi-change-positive" if change_sign > 0 else
        "kpi-change-negative" if change_sign < 0 else
        "kpi-change-neutral"
    )
    return html.Div([
        html.Div(label, className="kpi-label"),
        html.Div([
            html.Div([
                html.Span(value_str, className="kpi-value"),
                html.Span(unit, className="kpi-unit") if unit else None,
            ], className="d-flex align-items-baseline"),
            html.Span(change_str, className=f"kpi-change {change_class}") if change_str else None,
        ], className="d-flex align-items-baseline justify-content-between"),
    ], className="kpi-card")


def _pnl_pct(pnl, total_invested):
    """Return % return relative to total invested, or None if indeterminate."""
    if total_invested and total_invested != 0:
        return (pnl / total_invested) * 100
    return None


def kpi_row(data={}):
    currency = data.get("currency", "#")
    unit = "EUR" if currency == "EUR" else "USD"
    currency_sign = "€" if currency == "EUR" else "$"

    value = data.get("value", 0)
    total_invested = data.get("total_cost", 0)
    realized_pnl = data.get("realized_pnl", 0)
    unrealized_pnl = data.get("unrealized_pnl", 0)
    beta = data.get("beta", 1)
    cash = data.get("cash", 0)
    cash_pct = data.get("cash_pct", 0)

    unrealized_pct = _pnl_pct(unrealized_pnl, total_invested)
    realized_pct = _pnl_pct(realized_pnl, total_invested)

    return dbc.Row(
        [
            dbc.Col(_dark_kpi_card(
                "Portfolio Value",
                _fmt_currency(value, currency_sign),
                unit=unit,
            )),
            dbc.Col(_dark_kpi_card(
                "Total Invested",
                _fmt_currency(total_invested, currency_sign),
                unit=unit,
            )),
            dbc.Col(_dark_kpi_card(
                "Unrealized P&L",
                _fmt_currency(unrealized_pnl, currency_sign),
                unit=unit,
                change_str=_fmt_pct(unrealized_pct) if unrealized_pct is not None else "",
                change_sign=1 if unrealized_pnl > 0 else (-1 if unrealized_pnl < 0 else 0),
            )),
            dbc.Col(_dark_kpi_card(
                "Realized P&L",
                _fmt_currency(realized_pnl, currency_sign),
                unit=unit,
                change_str=_fmt_pct(realized_pct) if realized_pct is not None else "",
                change_sign=1 if realized_pnl > 0 else (-1 if realized_pnl < 0 else 0),
            )),
            dbc.Col(_dark_kpi_card(
                "Beta",
                f"{beta:.2f}",
                unit="vs Market",
                change_sign=0,
            )),
            dbc.Col(_dark_kpi_card(
                "Cash Available",
                _fmt_currency(cash, currency_sign),
                unit=unit,
                change_str=_fmt_pct(cash_pct),
                change_sign=0,
            )),
        ],
        className="mb-4 g-3 row-cols-2 row-cols-md-6"
    )
