import pandas as pd
from datetime import date, timedelta

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
    if not all([data, asset_name]):
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

    # Fall back to a 1-year window when the user hasn't set custom dates
    if not start_date:
        start_date = str(date.today() - timedelta(days=365))
    if not end_date:
        end_date = str(date.today())

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
    Output("asset_kpi_container", "children", allow_duplicate=True),
    Output("asset_page_chart_tab", "children", allow_duplicate=True),
    # Depreciated: Moved to portfolio page
    # Output("asset_tab", "children"),
    Input("active-page", "data"),
    State("asset_page_asset_store", "data"),
    prevent_initial_call=True,
)
def load_asset_page(pathname, cached_data):
    if pathname != "/assets":
        raise PreventUpdate

    cached_data = cached_data or {}
    view_model = cached_data.get("view_model", None)
    if view_model is None:
        view_model = AssetController().get_data()
        cached_data.update({"view_model": view_model})

    if view_model is None:
        raise PreventUpdate

    filter_data = view_model.get('asset_filter')
    asset_tickers = filter_data.get("rows", [])
    default_asset = asset_tickers[0] if asset_tickers else None

    if default_asset:
        asset_data = pd.DataFrame(view_model.get("asset_data"))
        mask = asset_data["ticker"].str.lower() == default_asset.lower()
        df_asset_data = asset_data[mask].to_dict("records")

        start_date = str(date.today() - timedelta(days=365))
        end_date = str(date.today())
        df_asset_data_history = AssetController().get_asset_snapshot(default_asset.lower(), start_date, end_date)

        kpi = asset_kpi_section(df_asset_data)
        charts = chart_tab(df_asset_data_history)
    else:
        from .components.kpi import asset_kpi_section_empty
        from .components.tabs import chart_tab_empty
        kpi = asset_kpi_section_empty()
        charts = chart_tab_empty()

    return (
        cached_data,
        asset_page_filter(filter_data, default_value=default_asset),
        kpi,
        charts,
    )
