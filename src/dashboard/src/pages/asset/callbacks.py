import pandas as pd

from dash import Input, Output, callback, State
from dash.exceptions import PreventUpdate

from ...controllers.asset_controller import AssetController

from .components.tabs import chart_tab
from .components.kpi import asset_kpi_section
from .components.filters import asset_page_filter

# ─────────────────────────────────────────────
# Callbacks
# ─────────────────────────────────────────────


@callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@callback(
    Output("asset_kpi_container", "children"),
    Output("asset_page_chart_tab", "children"),
    Input("asset_page_filter_btn", "n_clicks"),
    State("asset_page_asset_store", "data"),
    State("assetpage_asset_select", "value"),
    State("asset_page_date_picker_filter", "start_date"),
    State("asset_page_date_picker_filter", "end_date"),
    prevent_initial_call=True
)
def update_asset_page(n_clicks, data, asset_name, start_date, end_date):
    if not all([data, asset_name, start_date, end_date]):
        raise PreventUpdate

    # normalize the selected value once
    if isinstance(asset_name, str):
        asset_name = [asset_name]
    asset_key = [name.strip().lower() for name in asset_name]

    view_model = data.get("view_model")
    asset_data = pd.DataFrame(view_model.get("asset_data"))

    mask = asset_data["ticker"].str.lower().isin(asset_key)
    df_asset_data = asset_data[mask]

    df_asset_data = df_asset_data.to_dict("records")

    # TODO: UNCOMMENT TO CONNECT TO DB
    df_asset_data_history = AssetController().get_asset_snapshot(asset_key[0], start_date, end_date)

    # if df_asset_data_history.empty:
    #     raise PreventUpdate

    # if len(df_asset_data) == 0 or len(df_asset_data) == 0:
    #     raise PreventUpdate
    
    return (
        asset_kpi_section(df_asset_data),
        chart_tab(df_asset_data_history)
    )

@callback(
    Output("asset_page_asset_store", "data"),
    Output("asset_page_filter_container", "children"),
    # Depreciated: Moved to portfolio page
    # Output("asset_tab", "children"),
    Input("asset_page_location", "pathname"),
    State("asset_page_asset_store", "data"),
)
def load_asset_page(pathname, cached_data):
    if pathname != "/assets":
        raise PreventUpdate
    
    cached_data = cached_data or {}
    view_model =  cached_data.get("view_model", None)
    if view_model is None:
        view_model = AssetController().get_data()
        cached_data.update({"view_model": view_model})

    if view_model is None:
        raise PreventUpdate
    
    data = view_model.get('asset_filter')
    
    return (
        cached_data,
        asset_page_filter(data),
        # Depreciated: Moved to portfolio page
        # asset_table(df),
    )