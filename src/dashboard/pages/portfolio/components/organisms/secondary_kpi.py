"""Organism — secondary KPI rows shown on each tab and on asset selection."""

import dash_bootstrap_components as dbc
from dash import html

from ..atoms.badges import _kpi_badge, _tag_badge
from ..molecules.kpi_card import _daily_change_card


def secondary_kpi_row(data=None, theme="light"):
    data = data or {}
    daily_change_pct = data.get("daily_value_change_pct")
    daily_change_series = data.get("daily_change_series")
    portfolio_vol = data.get("portfolio_vol")

    return html.Div(
        [
            html.Div(
                [
                    _daily_change_card(daily_change_pct, daily_change_series, theme),
                    _kpi_badge(
                        "Volatility 30D",
                        f"{portfolio_vol:.2f}" if portfolio_vol is not None else "—",
                        unit="weighted",
                    ),
                ],
                className="kpi-badge-row",
            ),
        ],
        style={
            "paddingTop": "var(--ws-section-pad-v)",
            "marginBottom": "var(--ws-divider-v)",
        },
    )


def secondary_asset_kpi_row(ticker: str, metadata: dict):
    industry = metadata.get("industry") or "—"
    sector = metadata.get("sector") or "—"
    price = metadata.get("price")
    avg_price = metadata.get("avg_price")
    price_str = f"{price:.2f}" if price is not None else "—"
    avg_price_str = f"{avg_price:.2f}" if avg_price is not None else "—"

    return html.Div(
        [
            html.Div(
                [
                    _kpi_badge("Price", price_str),
                    _kpi_badge("AVG Price", avg_price_str),
                ],
                className="kpi-badge-row",
            ),
        ],
        className="asset-secondary-kpi",
        style={
            "paddingTop": "var(--ws-section-pad-v)",
            "marginBottom": "var(--ws-divider-v)",
        },
    )


def secondary_asset_tag_row(ticker: str, metadata: dict, accent: str = None):
    tags = metadata.get("tags", [])

    tag_badges = [_tag_badge(tag, accent=accent) for tag in tags]

    return html.Div(
        tag_badges
        + [
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
        style={
            "paddingTop": "var(--ws-section-pad-v)",
            "marginBottom": "var(--ws-divider-v)",
        },
    )
