import dash_bootstrap_components as dbc
from dash import dcc, html

from .callbacks import load_portfolio_page  # noqa: F401 — registers callback
from .components.kpis import kpi_row
from .components.tables import asset_table
from .components.filter_bar import workspace_filter_bar, workspace_advanced_filter
from .components.workspace_tabs import workspace_tabs


# ─────────────────────────────────────────────
# Page layout
# ─────────────────────────────────────────────

def portfolio_layout():
    return html.Div([
        dcc.Location(id="portfolio_page_location"),
        dcc.Store(id="portfolio_page_asset_store"),
        dcc.Store(id="workspace-selected-asset", data=[]),
        dcc.Store(id="workspace-timeframe", data="1Y"),
        dcc.Store(id="assign-tag-modal-ticker"),

        # ── Row 1: KPI Summary (always portfolio-scoped) ──────────
        dbc.Row([
            dcc.Loading(
                type="dot",
                children=dbc.Col(
                    id="portfolio_kpi_container",
                    children=kpi_row(),
                ),
            )
        ], className="mb-0"),

        # ── Row 2: Filter Controls ────────────────────────────────
        workspace_filter_bar(),
        workspace_advanced_filter(),

        # ── Row 3: Analysis Workspace (resizable split panels) ────
        html.Div(
            id="workspace-split",
            className="workspace-split",
            **{"data-initialized": ""},
            children=[
                # Left panel: asset table + footer
                html.Div(
                    id="workspace-left",
                    className="workspace-panel-left",
                    children=[
                        html.Div(
                            id="portfolio_page_asset_table_container",
                            children=asset_table(None),
                            style={"flex": "1", "minHeight": "0", "overflow": "hidden"},
                        ),
                        html.Div(
                            id="workspace-table-footer",
                            className="workspace-table-footer",
                            children="Loading assets…",
                        ),
                    ],
                ),

                # Drag divider
                html.Div(id="split-divider", className="split-divider"),

                # Right panel: chart header + tabs
                html.Div(
                    id="workspace-right",
                    className="workspace-panel-right",
                    **{"data-observer": ""},
                    children=[
                        workspace_tabs(),

                        # ── Edit Tags overlay — localized to workspace right panel ──
                        html.Div(
                            id="assign-tag-modal-overlay",
                            className="ws-modal-overlay",
                            style={"display": "none"},
                            children=html.Div([
                                html.Div([
                                    html.Span(id="assign-tag-modal-title", className="ws-modal-title"),
                                    html.Button("×", id="assign-tag-modal-close-btn", className="ws-modal-close"),
                                ], className="ws-modal-header"),
                                html.Div([
                                    html.Div([
                                        html.Label("Tag", className="ws-modal-label"),
                                        dcc.Dropdown(id="assign-tag-modal-tag-select", placeholder="Select tag…", className="ws-modal-dropdown"),
                                    ], className="mb-3"),
                                    html.Div([
                                        html.Label("Category", className="ws-modal-label"),
                                        dcc.Dropdown(id="assign-tag-modal-category-select", placeholder="Select category…", className="ws-modal-dropdown"),
                                    ], className="mb-3"),
                                ], className="ws-modal-body"),
                                html.Div([
                                    dbc.Button("Save", id="assign-tag-modal-save-btn", color="primary", size="sm"),
                                    html.Small("", id="assign-tag-modal-status", className="text-muted ms-3"),
                                ], className="ws-modal-footer"),
                            ], className="ws-modal-card"),
                        ),
                    ],
                ),
            ],
        ),
    ], id="portfolio-page-root")
