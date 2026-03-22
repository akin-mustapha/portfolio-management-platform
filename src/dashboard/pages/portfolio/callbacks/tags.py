"""
Tags modal callbacks — open, save, and close the Edit Tags overlay.
"""
from dash import ALL, Output, Input, State, callback, ctx, no_update
from dash.exceptions import PreventUpdate

from ....controllers.asset_profile_controller import AssetProfileController

_MODAL_SHOW = {"display": "flex"}
_MODAL_HIDE = {"display": "none"}


# ── 7. Edit Tags modal — open ─────────────────────────────────────

@callback(
    Output("assign-tag-modal-overlay",         "style"),
    Output("assign-tag-modal-title",           "children"),
    Output("assign-tag-modal-tag-select",      "options"),
    Output("assign-tag-modal-category-select", "options"),
    Output("assign-tag-modal-ticker",          "data"),
    Output("assign-tag-modal-status",          "children"),
    Input({"type": "assign-tag-btn", "index": ALL}, "n_clicks"),
    State("portfolio_page_asset_store", "data"),
    prevent_initial_call=True,
)
def open_assign_tag_modal(n_clicks_list, cached_data):
    if not any(n for n in n_clicks_list if n):
        raise PreventUpdate
    ticker = ctx.triggered_id["index"]
    asset_rows = (cached_data or {}).get("view_model", {}).get("asset_table", {}).get("rows", [])
    asset_row  = next((r for r in asset_rows if r.get("ticker") == ticker), {})
    vm = AssetProfileController().get_profile(asset_row)
    return _MODAL_SHOW, f"Assign Tags — {ticker.upper()}", vm["tag_options"], vm["category_options"], ticker, ""


# ── 8. Edit Tags modal — save ─────────────────────────────────────

@callback(
    Output("assign-tag-modal-status",  "children", allow_duplicate=True),
    Output("assign-tag-modal-overlay", "style",    allow_duplicate=True),
    Input("assign-tag-modal-save-btn", "n_clicks"),
    State("assign-tag-modal-tag-select", "value"),
    State("assign-tag-modal-ticker",     "data"),
    State("portfolio_page_asset_store",  "data"),
    prevent_initial_call=True,
)
def save_modal_tag(n_clicks, tag_id, ticker, cached_data):
    if not n_clicks or not ticker:
        raise PreventUpdate
    asset_rows = (cached_data or {}).get("view_model", {}).get("asset_table", {}).get("rows", [])
    asset_row  = next((r for r in asset_rows if r.get("ticker") == ticker), {})
    asset_name = asset_row.get("name", "")
    if tag_id and asset_name:
        AssetProfileController().assign_tag(asset_name, tag_id)
        return "Saved ✓", _MODAL_HIDE
    return "Nothing to save.", no_update


# ── 9. Edit Tags modal — close ────────────────────────────────────

@callback(
    Output("assign-tag-modal-overlay", "style", allow_duplicate=True),
    Input("assign-tag-modal-close-btn", "n_clicks"),
    prevent_initial_call=True,
)
def close_assign_tag_modal(n):
    return _MODAL_HIDE
