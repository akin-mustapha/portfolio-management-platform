"""Rebalancing config panel — left drawer with per-asset sliders."""
import dash_bootstrap_components as dbc
from dash import dcc, html


def rebalance_drawer_content():
    """Static shell — sliders are populated dynamically by the render_panel_body callback."""
    return html.Div([

        # Header
        html.Div([
            html.Span(
                [html.I(className="fa-solid fa-scale-balanced me-2"), "Rebalancing"],
                className="rebalance-panel-title",
            ),
        ], className="rebalance-panel-header"),

        html.Hr(className="tv-divider"),

        # Slider body — populated by callback
        html.Div(id="rebalance-panel-body", children=[
            html.P("Loading config…", className="text-muted", style={"fontSize": "12px", "padding": "8px"}),
        ]),

        html.Hr(className="tv-divider"),

        # Footer buttons
        html.Div([
            dbc.Button(
                "Save Config",
                id="rebalance-panel-save-btn",
                className="tv-apply-btn me-2",
                size="sm",
                n_clicks=0,
            ),
            dbc.Button(
                [html.I(className="fa-solid fa-bolt me-1"), "Generate Plan"],
                id="rebalance-panel-generate-btn",
                className="tv-ghost-btn",
                size="sm",
                n_clicks=0,
            ),
        ], className="rebalance-panel-footer"),

        html.Small("", id="rebalance-panel-status", className="text-muted rebalance-status-text"),

        html.Hr(className="tv-divider"),

        # Plan summary — populated by callback
        html.Div(id="rebalance-panel-plan-summary"),

    ], className="rebalance-drawer-inner")


def build_asset_sliders(configs: list[dict]) -> list:
    """Build one slider card per asset config row."""
    if not configs:
        return [html.P("No assets configured.", className="text-muted", style={"fontSize": "12px", "padding": "8px"})]

    cards = []
    for cfg in configs:
        ticker = cfg["ticker"]
        cards.append(
            html.Div([

                html.Div(ticker, className="rebalance-asset-name"),

                _slider_row("Target Weight %", {"type": "rebalance-slider", "index": f"{ticker}|target_weight_pct"},
                            0, 100, 0.5, cfg.get("target_weight_pct", 0)),

                html.Div([
                    html.Div([
                        html.Span("Min %", className="rebalance-slider-label"),
                        dcc.Slider(
                            id={"type": "rebalance-slider", "index": f"{ticker}|min_weight_pct"},
                            min=0, max=100, step=0.5,
                            value=cfg.get("min_weight_pct", 0),
                            marks=None,
                            tooltip={"placement": "bottom", "always_visible": False},
                            className="rebalance-slider",
                        ),
                    ], style={"flex": "1", "marginRight": "8px"}),
                    html.Div([
                        html.Span("Max %", className="rebalance-slider-label"),
                        dcc.Slider(
                            id={"type": "rebalance-slider", "index": f"{ticker}|max_weight_pct"},
                            min=0, max=100, step=0.5,
                            value=cfg.get("max_weight_pct", 100),
                            marks=None,
                            tooltip={"placement": "bottom", "always_visible": False},
                            className="rebalance-slider",
                        ),
                    ], style={"flex": "1"}),
                ], style={"display": "flex"}),

                _slider_row("Risk Tolerance", {"type": "rebalance-slider", "index": f"{ticker}|risk_tolerance"},
                            0, 100, 1, cfg.get("risk_tolerance", 50)),

                _slider_row("Correction Days", {"type": "rebalance-slider", "index": f"{ticker}|correction_days"},
                            1, 7, 1, cfg.get("correction_days", 3),
                            marks={i: str(i) for i in range(1, 8)}),

                _slider_row("Momentum Bias", {"type": "rebalance-slider", "index": f"{ticker}|momentum_bias"},
                            -100, 100, 1, cfg.get("momentum_bias", 0)),

            ], className="rebalance-asset-card")
        )
    return cards


def render_plan_summary(plan: dict | None) -> list:
    """Render the latest rebalance plan as a read-only summary."""
    if not plan or not plan.get("plan_json"):
        return [html.P("No plan generated yet.", className="text-muted", style={"fontSize": "12px"})]

    pj = plan["plan_json"]
    rows = [
        html.Div("Latest Plan", className="tv-section-header"),
        html.Small(
            f"{plan.get('created_date', '')} · {pj.get('summary', '')}",
            className="text-muted d-block mb-2",
            style={"fontSize": "11px"},
        ),
    ]
    for action in pj.get("actions", []):
        drift = action.get("drift_pct", 0)
        sign = "+" if drift > 0 else ""
        rows.append(
            html.Div([
                html.Span(action["ticker"], className="rebalance-plan-ticker"),
                html.Span(
                    action["action"].upper(),
                    className=f"rebalance-plan-action {'rebalance-action-reduce' if action['action'] == 'reduce' else 'rebalance-action-increase'}",
                ),
                html.Span(
                    f"{action['current_weight_pct']:.1f}% → {action['target_weight_pct']:.1f}%  ({sign}{drift:.1f}%)",
                    className="rebalance-plan-detail",
                ),
            ], className="rebalance-plan-row")
        )
    return rows


# ── Private helper ────────────────────────────────────────────────────────────

def _slider_row(label: str, slider_id, min_val, max_val, step, value, marks=None):
    return html.Div([
        html.Span(label, className="rebalance-slider-label"),
        dcc.Slider(
            id=slider_id,
            min=min_val, max=max_val, step=step,
            value=value,
            marks=marks,
            tooltip={"placement": "bottom", "always_visible": False},
            className="rebalance-slider",
        ),
    ], className="rebalance-slider-row")
