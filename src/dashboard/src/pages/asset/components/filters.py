from dash import dcc, html
import dash_bootstrap_components as dbc
from datetime import date, datetime, timedelta

TIMEFRAMES = {
    0: ("1D", 0),
    1: ("1W", 7),
    2: ("1M", 30),
    3: ("3M", 90),
    4: ("6M", 180),
    5: ("1Y", 365),
    6: ("ALL", None),
}

_FONT = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
_BORDER = "1px solid #e0e3eb"
_RADIUS = "4px"


def asset_page_filter(data, default_value=None):
    today = date.today()

    return html.Div(
        [
            # ── Filter bar (single horizontal row) ────────────────────────────
            html.Div(
                [
                    # Symbol dropdown
                    html.Div(
                        dcc.Dropdown(
                            options=data.get("rows", []),
                            value=default_value,
                            multi=False,
                            placeholder="Search symbol…",
                            id="assetpage_asset_select",
                            searchable=True,
                            clearable=True,
                            style={"width": "100%", "fontFamily": _FONT},
                        ),
                        style={"width": "160px", "flexShrink": "0"},
                    ),

                    # Vertical divider
                    html.Div(className="tv-vert-divider", style={
                        "width": "1px", "height": "20px",
                        "background": "#e0e3eb",
                        "margin": "0 16px", "flexShrink": "0",
                        "alignSelf": "center",
                    }),

                    # "Timeframe" label
                    html.Span(
                        "Timeframe",
                        className="tv-filter-label",
                        style={
                            "fontSize": "11px", "fontWeight": "600",
                            "textTransform": "uppercase",
                            "letterSpacing": "0.5px", "whiteSpace": "nowrap",
                            "flexShrink": "0", "fontFamily": _FONT,
                            "marginRight": "6px",
                        },
                    ),

                    # Timeframe buttons — no color/background inline so CSS hover works
                    dcc.RadioItems(
                        id="date-slider",
                        options=[
                            {"label": label, "value": key}
                            for key, (label, _) in TIMEFRAMES.items()
                        ],
                        value=0,
                        inline=True,
                        className="tv-timeframe-strip",
                        inputStyle={
                            "position": "absolute",
                            "opacity": "0",
                            "width": "0",
                            "height": "0",
                            "margin": "0",
                            "pointerEvents": "none",
                        },
                        labelStyle={
                            "display": "inline-block",
                            "padding": "3px 10px",
                            "borderRadius": _RADIUS,
                            "fontSize": "13px",
                            "fontWeight": "500",
                            "cursor": "pointer",
                            "userSelect": "none",
                            "fontFamily": _FONT,
                            "margin": "0 1px",
                            "lineHeight": "1.6",
                        },
                    ),

                    # Advanced Filter — right-aligned
                    html.Div(
                        dbc.Button(
                            "Advanced Filter",
                            id="collapse-button",
                            n_clicks=0,
                            className="tv-adv-btn",
                            color="link",
                        ),
                        style={"marginLeft": "auto", "flexShrink": "0"},
                    ),
                ],
                style={
                    "display": "flex",
                    "flexDirection": "row",
                    "alignItems": "center",
                    "padding": "6px 14px",
                    "minHeight": "48px",
                },
            ),

            # ── Collapsible date range ─────────────────────────────────────────
            dbc.Collapse(
                html.Div(
                    [
                        html.Span("From", className="tv-date-label"),
                        dcc.DatePickerSingle(
                            id="asset_page_date_picker_filter",
                            min_date_allowed=date(2020, 1, 1),
                            max_date_allowed=date(2049, 12, 31),
                            date=str(today - timedelta(days=1)),
                            display_format="YYYY-MM-DD",
                            className="tv-single-picker",
                        ),
                        html.Span("→", className="tv-filter-label", style={
                            "fontFamily": _FONT,
                            "fontSize": "14px", "flexShrink": "0",
                        }),
                        html.Span("To", className="tv-date-label"),
                        dcc.DatePickerSingle(
                            id="asset_page_end_date_picker_filter",
                            min_date_allowed=date(2020, 1, 1),
                            max_date_allowed=date(2049, 12, 31),
                            date=str(today),
                            display_format="YYYY-MM-DD",
                            className="tv-single-picker",
                        ),
                        dbc.Button(
                            "Apply",
                            id="asset_page_filter_btn",
                            n_clicks=0,
                            className="tv-apply-btn",
                            color="link",
                        ),
                    ],
                    className="tv-collapse-body",
                ),
                id="collapse",
                is_open=False,
            ),
        ],
        className="asset-filter-bar",
        style={
            "background": "#fff",
            "border": _BORDER,
            "borderRadius": "6px",
            "marginBottom": "16px",
            "fontFamily": _FONT,
        },
    )
