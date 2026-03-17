import dash_bootstrap_components as dbc
from dash import dcc, html

from . import callbacks  # noqa: F401 — registers Dash callbacks

from .components.kpi import asset_kpi_section_empty
from .components.tabs import chart_tab_empty
from ...styles.style import TAB_CONTENT_STYLE


def page_content():
    return dbc.Tabs([
        # Depreciated: Moved to portfolio page
        # dbc.Tab(id="asset_tab", children=[dag.AgGrid()], label="Assets", style=TAB_CONTENT_STYLE),
        dbc.Tab(id="asset_chart_tab", children=chart_tab_empty(), label="Charts", style=TAB_CONTENT_STYLE),
    ])
    

# ─────────────────────────────────────────────
# Page layout
# ─────────────────────────────────────────────
def asset_layout():
    return html.Div([
        dcc.Store(id="asset_page_asset_store"),

        dbc.Row([
            dbc.Stack([
                html.Div(id="asset_kpi_container", children=[asset_kpi_section_empty()]),
                html.Div(id="asset_page_filter_container")
            ], gap=4)
        ]),

        dbc.Row(id="asset_page_content_container", children=[page_content()]),
    ], id="asset_page")
