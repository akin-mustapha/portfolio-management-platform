"""Rebalancing panel callbacks — toggle, load, save, generate plan."""
from dash import callback, Input, Output, State, ALL, no_update
from dash.exceptions import PreventUpdate

from backend.services.rebalancing.rebalancing_service_builder import build_rebalancing_service
from backend.services.rebalancing.domain.entities import RebalanceConfig

from ..components.organisms.rebalance_panel import build_asset_sliders, render_plan_summary
from ..components.organisms.rebalance_panel import build_single_asset_sliders, render_plan_summary


# ── 1. Toggle panel visibility ────────────────────────────────────────────────

@callback(
    Output("rebalance-panel-wrapper", "style"),
    Input("rebalance-panel-toggle-btn", "n_clicks"),
    State("rebalance-panel-wrapper", "style"),
    prevent_initial_call=True,
)
def toggle_rebalance_panel(n_clicks, current_style):
    is_visible = (current_style or {}).get("display") != "none"
    return {"display": "none"} if is_visible else {"display": "flex"}


# ── 2. Load configs + latest plan on page load ────────────────────────────────

@callback(
    Output("rebalance-config-store", "data"),
    Input("portfolio_page_location", "pathname"),
)
def load_rebalance_data(_pathname):
    service = build_rebalancing_service()
    configs = service.load_configs()
    plan = service.get_latest_plan()
    return {
        "configs": [
            {
                "id": c.id,
                "asset_id": c.asset_id,
                "ticker": c.ticker,
                "target_weight_pct": c.target_weight_pct,
                "min_weight_pct": c.min_weight_pct,
                "max_weight_pct": c.max_weight_pct,
                "risk_tolerance": c.risk_tolerance,
                "rebalance_threshold_pct": c.rebalance_threshold_pct,
                "correction_days": c.correction_days,
                "momentum_bias": c.momentum_bias,
                "is_active": c.is_active,
            }
            for c in configs
        ],
        "plan": plan,
    }


# ── 3. Render sliders and plan summary from store ─────────────────────────────

@callback(
    Output("rebalance-panel-body", "children"),
    Output("rebalance-panel-plan-summary", "children"),
    Input("rebalance-config-store", "data"),
)
def render_panel(store_data):
    if not store_data:
        raise PreventUpdate
    sliders = build_asset_sliders(store_data.get("configs", []))
    plan_summary = render_plan_summary(store_data.get("plan"))
    return sliders, plan_summary


# ── 4. Save slider values to DB ───────────────────────────────────────────────
    Output("rebalance-asset-select", "options"),
    Input("portfolio_page_location", "pathname"),
)
def load_rebalance_data(_pathname):
    try:
        service = build_rebalancing_service()
        configs = service.load_configs()
        plan = service.get_latest_plan()
        options = [{"label": c.ticker, "value": c.ticker} for c in configs]
        store = {
            "configs": [
                {
                    "id": c.id,
                    "asset_id": c.asset_id,
                    "ticker": c.ticker,
                    "target_weight_pct": c.target_weight_pct,
                    "min_weight_pct": c.min_weight_pct,
                    "max_weight_pct": c.max_weight_pct,
                    "risk_tolerance": c.risk_tolerance,
                    "rebalance_threshold_pct": c.rebalance_threshold_pct,
                    "correction_days": c.correction_days,
                    "momentum_bias": c.momentum_bias,
                    "is_active": c.is_active,
                }
                for c in configs
            ],
            "plan": plan,
        }
        return store, options
    except Exception as e:
        return {"configs": [], "plan": None, "error": str(e)}, []


# ── 3. Render sliders for selected asset ──────────────────────────────────────

@callback(
    Output("rebalance-panel-body", "children"),
    Input("rebalance-asset-select", "value"),
    State("rebalance-config-store", "data"),
    prevent_initial_call=True,
)
def render_selected_asset_sliders(ticker, store_data):
    if not ticker or not store_data:
        raise PreventUpdate
    cfg = next((c for c in store_data.get("configs", []) if c["ticker"] == ticker), None)
    if not cfg:
        raise PreventUpdate
    return build_single_asset_sliders(cfg)


# ── 4. Render plan summary on store load ──────────────────────────────────────

@callback(
    Output("rebalance-panel-plan-summary", "children"),
    Input("rebalance-config-store", "data"),
)
def render_plan_on_load(store_data):
    if not store_data:
        raise PreventUpdate
    return render_plan_summary(store_data.get("plan"))


# ── 5. Save slider values to DB ───────────────────────────────────────────────

@callback(
    Output("rebalance-panel-status", "children"),
    Input("rebalance-panel-save-btn", "n_clicks"),
    State({"type": "rebalance-slider", "index": ALL}, "value"),
    State({"type": "rebalance-slider", "index": ALL}, "id"),
    State("rebalance-config-store", "data"),
    prevent_initial_call=True,
)
def save_configs(n_clicks, values, ids, store_data):
    if not n_clicks or not store_data:
        raise PreventUpdate

    # Build {ticker: {field: value}} from the pattern-matched sliders
    asset_fields: dict[str, dict] = {}
    for slider_id, value in zip(ids, values):
        index = slider_id["index"]          # e.g. "NVDA|target_weight_pct"
        ticker, field = index.split("|", 1)
        asset_fields.setdefault(ticker, {})[field] = value

    # Build asset_id lookup from store
    asset_fields: dict[str, dict] = {}
    for slider_id, value in zip(ids, values):
        index = slider_id["index"]
        parts = index.split("|", 1)
        if len(parts) != 2:
            continue
        ticker, field = parts
        asset_fields.setdefault(ticker, {})[field] = value

    asset_id_by_ticker = {c["ticker"]: c["asset_id"] for c in store_data.get("configs", [])}
    existing_by_ticker = {c["ticker"]: c for c in store_data.get("configs", [])}

    service = build_rebalancing_service()
    try:
        for ticker, fields in asset_fields.items():
            asset_id = asset_id_by_ticker.get(ticker)
            if not asset_id:
                continue
            existing = existing_by_ticker.get(ticker, {})
            config = RebalanceConfig(
                id=existing.get("id"),
                asset_id=asset_id,
                ticker=ticker,
                target_weight_pct=fields.get("target_weight_pct", existing.get("target_weight_pct", 0)),
                min_weight_pct=fields.get("min_weight_pct", existing.get("min_weight_pct", 0)),
                max_weight_pct=fields.get("max_weight_pct", existing.get("max_weight_pct", 100)),
                risk_tolerance=int(fields.get("risk_tolerance", existing.get("risk_tolerance", 50))),
                rebalance_threshold_pct=existing.get("rebalance_threshold_pct", 2.0),
                correction_days=int(fields.get("correction_days", existing.get("correction_days", 3))),
                momentum_bias=int(fields.get("momentum_bias", existing.get("momentum_bias", 0))),
                is_active=existing.get("is_active", True),
            )
            service.upsert_config(config)
        return "Saved ✓"
    except Exception as e:
        return f"Error: {e}"


# ── 5. Generate plan on demand ────────────────────────────────────────────────
# ── 6. Generate plan on demand ────────────────────────────────────────────────

@callback(
    Output("rebalance-panel-plan-summary", "children", allow_duplicate=True),
    Output("rebalance-panel-status", "children", allow_duplicate=True),
    Input("rebalance-panel-generate-btn", "n_clicks"),
    prevent_initial_call=True,
)
def generate_plan_on_demand(n_clicks):
    if not n_clicks:
        raise PreventUpdate
    service = build_rebalancing_service()
    try:
        plan = service.generate_and_save_plan()
        if plan is None:
            return render_plan_summary(None), "All assets within threshold — no plan needed"
        latest = service.get_latest_plan()
        return render_plan_summary(latest), "Plan generated ✓"
    except Exception as e:
        return no_update, f"Error: {e}"
