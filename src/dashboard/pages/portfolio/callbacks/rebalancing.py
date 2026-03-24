"""Rebalancing panel callbacks — toggle, load, save, generate plan."""

from dash import callback, html, Input, Output, State, ALL, no_update
from dash.exceptions import PreventUpdate

from backend.services.rebalancing.rebalancing_service_builder import (
    build_rebalancing_service,
)
from backend.services.rebalancing.domain.entities import RebalanceConfig

from ..components.organisms.rebalance_panel import (
    build_asset_sliders,
    render_plan_summary,
)

# ── 0a. Populate dropdown options from asset store ────────────────────────────


@callback(
    Output("rebalance-asset-select", "options"),
    Input("portfolio_page_asset_store", "data"),
)
def on_asset_store_change(store_data):
    rows = (
        (store_data or {}).get("view_model", {}).get("asset_table", {}).get("rows", [])
    )
    return [
        {"label": r["ticker"], "value": r["ticker"]} for r in rows if r.get("ticker")
    ]


# ── 0b. Render sliders for selected asset ─────────────────────────────────────


@callback(
    Output("rebalance-panel-body", "children"),
    Input("rebalance-asset-select", "value"),
    State("rebalance-config-store", "data"),
)
def on_asset_select(ticker, store_data):
    if not ticker:
        return html.P(
            "Select an asset above.",
            className="text-muted",
            style={"fontSize": "12px", "padding": "8px"},
        )
    configs = (store_data or {}).get("configs", [])
    asset_config = next(
        (c for c in configs if c["ticker"] == ticker), {"ticker": ticker}
    )
    return build_asset_sliders([asset_config])


# ── 1. Toggle panel visibility ────────────────────────────────────────────────


@callback(
    Output("rebalance-panel-wrapper", "style"),
    Input("rebalance-panel-toggle-btn", "n_clicks"),
    State("rebalance-panel-wrapper", "style"),
    prevent_initial_call=True,
)
def on_toggle_rebalance(n_clicks, current_style):
    is_visible = (current_style or {}).get("display") != "none"
    return {"display": "none"} if is_visible else {"display": "flex"}


# ── 2. Load configs + latest plan on page load ────────────────────────────────


@callback(
    Output("rebalance-config-store", "data"),
    Output("rebalance-panel-plan-summary", "children"),
    Input("portfolio_page_location", "pathname"),
)
def on_page_load(_pathname):
    try:
        service = build_rebalancing_service()
        configs = service.load_configs()
        plan = service.get_latest_plan()
        return _build_store(configs, plan), render_plan_summary(plan)
    except Exception as e:
        return {"configs": [], "plan": None, "error": str(e)}, render_plan_summary(None)


# ── 4. Save slider values to DB ───────────────────────────────────────────────


@callback(
    Output("rebalance-panel-status", "children"),
    Output("rebalance-config-store", "data", allow_duplicate=True),
    Output("rebalance-panel-body", "children", allow_duplicate=True),
    Input("rebalance-panel-save-btn", "n_clicks"),
    State({"type": "rebalance-slider", "index": ALL}, "value"),
    State({"type": "rebalance-slider", "index": ALL}, "id"),
    State("rebalance-config-store", "data"),
    State("rebalance-asset-select", "value"),
    prevent_initial_call=True,
)
def on_save_configs(n_clicks, values, ids, store_data, current_ticker):
    if not n_clicks or not store_data:
        raise PreventUpdate

    asset_fields: dict[str, dict] = {}
    for slider_id, value in zip(ids, values):
        index = slider_id["index"]  # e.g. "NVDA|target_weight_pct"
        ticker, field = index.split("|", 1)
        asset_fields.setdefault(ticker, {})[field] = value

    existing_by_ticker = {c["ticker"]: c for c in store_data.get("configs", [])}

    try:
        service = build_rebalancing_service()
        for ticker, fields in asset_fields.items():
            existing = existing_by_ticker.get(ticker, {})
            asset_id = existing.get("asset_id") or service.get_asset_id_by_ticker(
                ticker
            )
            if not asset_id:
                return (
                    f"Error: asset ID not found for {ticker} — try reloading the page.",
                    no_update,
                    no_update,
                )

            target = fields.get(
                "target_weight_pct", existing.get("target_weight_pct", 5)
            )
            band = fields.get(
                "tolerance_band_pct", existing.get("tolerance_band_pct", 5)
            )
            config = RebalanceConfig(
                id=existing.get("id"),
                asset_id=asset_id,
                ticker=ticker,
                target_weight_pct=target,
                min_weight_pct=max(0.0, target - band),
                max_weight_pct=min(50.0, target + band),
                rebalance_threshold_pct=float(
                    fields.get(
                        "rebalance_threshold_pct",
                        existing.get("rebalance_threshold_pct", 2.0),
                    )
                ),
                correction_days=int(
                    fields.get("correction_days", existing.get("correction_days", 7))
                ),
                is_active=existing.get("is_active", True),
            )

            service.upsert_config(config)

        # Reload from DB — source of truth after upsert
        refreshed_configs = service.load_configs()
        refreshed_store = _build_store(refreshed_configs, store_data.get("plan"))

        # Re-render sliders from saved DB values so user gets visual confirmation
        refreshed_sliders = no_update
        if current_ticker:
            saved_cfg = next(
                (c for c in refreshed_configs if c.ticker == current_ticker), None
            )
            if saved_cfg:
                refreshed_sliders = build_asset_sliders(
                    [
                        {
                            "ticker": saved_cfg.ticker,
                            "target_weight_pct": saved_cfg.target_weight_pct,
                            "tolerance_band_pct": round(
                                (saved_cfg.max_weight_pct - saved_cfg.min_weight_pct)
                                / 2,
                                1,
                            ),
                            "rebalance_threshold_pct": saved_cfg.rebalance_threshold_pct,
                            "correction_days": saved_cfg.correction_days,
                            "is_active": saved_cfg.is_active,
                        }
                    ]
                )

        return "Saved", refreshed_store, refreshed_sliders
    except Exception as e:
        return f"Error: {e}", no_update, no_update


# ── 5. Generate plan on demand ────────────────────────────────────────────────


@callback(
    Output("rebalance-panel-plan-summary", "children", allow_duplicate=True),
    Output("rebalance-panel-status", "children", allow_duplicate=True),
    Input("rebalance-panel-generate-btn", "n_clicks"),
    prevent_initial_call=True,
)
def on_generate_plan(n_clicks):
    if not n_clicks:
        raise PreventUpdate
    service = build_rebalancing_service()
    try:
        plan = service.generate_and_save_plan()
        if plan is None:
            return (
                render_plan_summary(None),
                "All assets within threshold — no plan needed",
            )
        latest = service.get_latest_plan()
        status = (
            "Plan generated ✓"
            if latest
            else "Plan generated but could not be retrieved"
        )
        return render_plan_summary(latest), status
    except Exception as e:
        return no_update, f"Error: {e}"


# ── Private helper ────────────────────────────────────────────────────────────


def _build_store(configs, plan) -> dict:
    return {
        "configs": [
            {
                "id": c.id,
                "asset_id": c.asset_id,
                "ticker": c.ticker,
                "target_weight_pct": c.target_weight_pct,
                "min_weight_pct": c.min_weight_pct,
                "max_weight_pct": c.max_weight_pct,
                "tolerance_band_pct": round(
                    (c.max_weight_pct - c.min_weight_pct) / 2, 1
                ),
                "rebalance_threshold_pct": c.rebalance_threshold_pct,
                "correction_days": c.correction_days,
                "is_active": c.is_active,
            }
            for c in configs
        ],
        "plan": plan,
    }
