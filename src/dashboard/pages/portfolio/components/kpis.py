import dash_bootstrap_components as dbc
from dash import dcc, html

from ..charts.portfolio_charts import daily_change_sparkline


def _fmt_currency(value, sign):
    return f"{sign}{value:,.2f}"


def _fmt_pct(value):
    prefix = "+" if value > 0 else ""
    return f"{prefix}{value:.2f}%"


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


def _kpi_badge(label, value_str, unit="", change_sign=0):
    change_class = (
        "kpi-change-positive" if change_sign > 0 else
        "kpi-change-negative" if change_sign < 0 else
        "kpi-change-neutral"
    )
    return html.Div([
        html.Span(label, className="kpi-badge__label"),
        html.Div([
            html.Span(value_str, className=f"kpi-badge__value {change_class}"),
            html.Span(unit, className="kpi-badge__unit") if unit else None,
        ], className="d-flex align-items-baseline gap-1"),
    ], className="kpi-badge")


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


def _tag_badge(value_str, accent=None):
    style = {"borderColor": accent, "color": accent} if accent else {}
    return html.Div(
        html.Span(value_str, className="tag-badge__value"),
        className="tag-badge",
        style=style,
    )

def secondary_asset_kpi_row(ticker: str, metadata: dict):
    industry = metadata.get("industry") or "—"
    sector = metadata.get("sector") or "—"
    price = metadata.get("price")
    avg_price = metadata.get("avg_price")
    price_str = f"{price:.4f}" if price is not None else "—"
    avg_price_str = f"{avg_price:.4f}" if avg_price is not None else "—"

    return html.Div([
        html.Div([
            _kpi_badge("Industry", industry),
            _kpi_badge("Sector", sector),
            _kpi_badge("Price", price_str),
            _kpi_badge("AVG Price", avg_price_str),
        ], className="kpi-badge-row"),
    ], className="asset-secondary-kpi", style={"paddingTop": "var(--ws-section-pad-v)", "marginBottom": "var(--ws-divider-v)"})


def secondary_asset_tag_row(ticker: str, metadata: dict, accent: str = None):
    tags = metadata.get("tags", [])

    tag_badges = [_tag_badge(tag, accent=accent) for tag in tags]

    return html.Div(
        tag_badges + [
            dbc.Button(
                [html.I(className="fa-solid fa-tag me-1"), "Edit Tags"],
                id={"type": "assign-tag-btn", "index": ticker},
                size="sm",
                color="link",
                className="kpi-badge kpi-badge--action",
                n_clicks=0,
            ),
        ],
        className="tag-row",
        style={"paddingTop": "var(--ws-section-pad-v)", "marginBottom": "var(--ws-divider-v)"},
    )


def secondary_kpi_row(data=None, theme="light"):
    data = data or {}
    daily_change_pct = data.get("daily_change_pct")
    daily_change_series = data.get("daily_change_series")
    portfolio_vol = data.get("portfolio_vol")

    return html.Div([
        html.Div([
            _daily_change_card(daily_change_pct, daily_change_series, theme),
            _kpi_badge(
                "Volatility 30D",
                f"{portfolio_vol:.4f}" if portfolio_vol is not None else "—",
                unit="weighted",
            ),
        ], className="kpi-badge-row"),
    ], style={"paddingTop": "var(--ws-section-pad-v)", "marginBottom": "var(--ws-divider-v)"})
