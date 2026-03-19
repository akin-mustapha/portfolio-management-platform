import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash import dcc, html


# ─────────────────────────────────────────────
# Page layout
# ─────────────────────────────────────────────

def tag_layout():
    return html.Div([
        dcc.Location(id="tag_page_location"),
        dcc.Store(id="tag-page-store"),

        dbc.Row([

            # ── Left column: asset table + assign row ─────────────────
            dbc.Col([
                dag.AgGrid(
                    id="tag-page-asset-table",
                    rowData=[],
                    columnDefs=[
                        {"field": "ticker", "width": 90},
                        {"field": "name", "width": 150},
                        {
                            "field": "value",
                            "width": 100,
                            "valueFormatter": {"function": "d3.format(',.2f')(params.value)"},
                        },
                        {
                            "field": "profit",
                            "width": 100,
                            "valueFormatter": {"function": "d3.format(',.2f')(params.value)"},
                        },
                    ],
                    className="ag-theme-alpine",
                    style={"height": "480px"},
                ),

                dbc.Row([
                    dbc.Col(
                        dcc.Dropdown(
                            id="tag-page-tag-select",
                            placeholder="Select a tag…",
                            options=[],
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Assign Tag",
                            id="tag-page-assign-btn",
                            color="primary",
                            size="sm",
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        html.Small(id="tag-page-assign-status", children=""),
                        width=True,
                        className="d-flex align-items-center",
                    ),
                ], className="mt-2 align-items-center"),

            ], width=8),

            # ── Right column: management panels ───────────────────────
            dbc.Col([
                dbc.Accordion([

                    # 1. Create Industry
                    dbc.AccordionItem(
                        title="Create Industry",
                        children=[
                            dbc.Stack([
                                dbc.Input(
                                    id="input-industry-name",
                                    placeholder="Industry name",
                                    size="sm",
                                ),
                                dbc.Input(
                                    id="input-industry-description",
                                    placeholder="Description (optional)",
                                    size="sm",
                                ),
                                dbc.Button(
                                    "Create",
                                    id="btn-create-industry",
                                    color="primary",
                                    size="sm",
                                ),
                                html.Small(id="industry-create-status", children=""),
                            ], gap=2),
                        ],
                    ),

                    # 2. Create Sector
                    dbc.AccordionItem(
                        title="Create Sector",
                        children=[
                            dbc.Stack([
                                dbc.Input(
                                    id="input-sector-name",
                                    placeholder="Sector name",
                                    size="sm",
                                ),
                                dbc.Input(
                                    id="input-sector-description",
                                    placeholder="Description (optional)",
                                    size="sm",
                                ),
                                dcc.Dropdown(
                                    id="sector-industry-select",
                                    placeholder="Assign to industry…",
                                    options=[],
                                ),
                                dbc.Button(
                                    "Create",
                                    id="btn-create-sector",
                                    color="primary",
                                    size="sm",
                                ),
                                html.Small(id="sector-create-status", children=""),
                            ], gap=2),
                        ],
                    ),

                    # 3. Create Tag
                    dbc.AccordionItem(
                        title="Create Tag",
                        children=[
                            dbc.Stack([
                                dbc.Input(
                                    id="input-tag-name",
                                    placeholder="Tag name",
                                    size="sm",
                                ),
                                dbc.Input(
                                    id="input-tag-description",
                                    placeholder="Description (optional)",
                                    size="sm",
                                ),
                                dcc.Dropdown(
                                    id="tag-category-select",
                                    placeholder="Select category…",
                                    options=[],
                                ),
                                dbc.Button(
                                    "Create",
                                    id="btn-create-tag",
                                    color="primary",
                                    size="sm",
                                ),
                                html.Small(id="tag-create-status", children=""),
                            ], gap=2),
                        ],
                    ),

                ], always_open=True),
            ], width=4),

        ], className="mt-4"),
    ])
