"""Rebalancing config panel — left drawer with per-asset sliders."""
import dash_bootstrap_components as dbc
from dash import dcc, html

from ..atoms.dropdown import tv_dropdown


def rebalance_drawer_content():
    """Drawer shell with asset selector. Sliders populated by callback."""
    return html.Div([
        # Header
        html.Div([
            html.Span(
                [html.I(className="fa-solid fa-scale-balanced me-2"), "Rebalancing"],
                className="rebalance-panel-title",
            ),
        ], className="rebalance-panel-header"),

        html.Hr(className="tv-divider"),

        # Asset selector dropdown
        tv_dropdown(
            id="rebalance-asset-select",
            placeholder="Select an asset…",
            clearable=False,
            className="rebalance-asset-dropdown",
            style={"marginBottom": "12px"},
        ),

        # Slider body — populated by callback when asset is selected
        html.Div(id="rebalance-panel-body", children=html.P(
            "Select an asset above.",
            className="text-muted",
            style={"fontSize": "12px", "padding": "8px"},
        )),

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
                            0, 50, 1, cfg.get("target_weight_pct", 5)),

                _slider_row("Drift Threshold %", {"type": "rebalance-slider", "index": f"{ticker}|rebalance_threshold_pct"},
                            0, 20, 1, cfg.get("rebalance_threshold_pct", 2.0)),

                _slider_row("Tolerance Band %", {"type": "rebalance-slider", "index": f"{ticker}|tolerance_band_pct"},
                            0, 25, 1, cfg.get("tolerance_band_pct", 5)),

                _slider_row("Correction Days", {"type": "rebalance-slider", "index": f"{ticker}|correction_days"},
                            1, 30, 1, cfg.get("correction_days", 7),
                            marks={1: "1", 7: "7", 14: "14", 21: "21", 30: "30"}),

            ], className="rebalance-asset-card")
        )
    return cards


def render_plan_summary(plan: dict | None) -> list:
    """Render the latest rebalance plan as a read-only summary."""
    if not plan or not plan.get("plan_json"):
        return [html.P("No plan generated yet.", className="text-muted", style={"fontSize": "12px"})]

    pj = plan["plan_json"]
    actions = pj.get("actions", [])

    reduces = [a for a in actions if a["action"] == "reduce"]
    increases = [a for a in actions if a["action"] == "increase"]

    rows = [
        html.Div("Latest Plan", className="tv-section-header"),
        html.Small(plan.get("created_date", ""), className="text-muted d-block", style={"fontSize": "11px"}),
        html.Small(pj.get("summary", ""), className="d-block mb-1", style={"fontSize": "11px", "color": "var(--text-secondary)"}),
        # Stats bar
        html.Div([
            html.Span(
                f"↓ {len(reduces)} reduce",
                className="rebalance-action-reduce rebalance-plan-action",
            ) if reduces else None,
            html.Span(
                f"↑ {len(increases)} increase",
                className="rebalance-action-increase rebalance-plan-action",
            ) if increases else None,
        ], className="rebalance-plan-stats"),
    ]

    def _action_rows(group):
        out = []
        for action in group:
            drift = action.get("drift_pct", 0)
            sign = "+" if drift > 0 else ""
            is_reduce = action["action"] == "reduce"
            out.append(
                html.Div([
                    html.Span(action["ticker"], className="rebalance-plan-ticker"),
                    html.Span(
                        action["action"].upper(),
                        className=f"rebalance-plan-action {'rebalance-action-reduce' if is_reduce else 'rebalance-action-increase'}",
                    ),
                    html.Span(
                        f"{action['current_weight_pct']:.1f}% → {action['target_weight_pct']:.1f}%",
                        className="rebalance-plan-weight",
                    ),
                    html.Span(
                        f"{sign}{drift:.1f}%",
                        className=f"rebalance-plan-delta {'negative' if is_reduce else 'positive'}",
                    ),
                ], className="rebalance-plan-row")
            )
        return out

    if reduces:
        rows.append(html.Div("Reduce", className="rebalance-plan-group-label"))
        rows.extend(_action_rows(reduces))
    if increases:
        rows.append(html.Div("Increase", className="rebalance-plan-group-label"))
        rows.extend(_action_rows(increases))

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
            tooltip={"always_visible": False},
            updatemode='drag',
            className="rebalance-slider",
        ),
    ], className="rebalance-slider-row")
