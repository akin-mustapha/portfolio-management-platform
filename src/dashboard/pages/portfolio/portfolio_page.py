import dash_bootstrap_components as dbc
from dash import dcc, html

from .components.atoms.dropdown import tv_dropdown

from .callbacks import load_portfolio_page  # noqa: F401 — registers callback
from .components.organisms.kpi_row import kpi_row
from .components.organisms.asset_table import asset_table
from .components.organisms.filter_bar import (
    workspace_filter_bar,
    workspace_advanced_filter,
    column_visibility_popover,
    DEFAULT_VISIBLE_COLS,
)
from .components.organisms.workspace_tabs import workspace_tabs
from .components.organisms.rebalance_panel import rebalance_drawer_content

# ─────────────────────────────────────────────
# Page layout
# ─────────────────────────────────────────────


def portfolio_layout():
    return html.Div(
        [
            dcc.Location(id="portfolio_page_location"),
            dcc.Store(id="portfolio_page_asset_store"),
            dcc.Store(id="workspace-selected-asset", data=[]),
            dcc.Store(id="workspace-timeframe", data="1Y"),
            dcc.Store(id="assign-tag-modal-ticker"),
            dcc.Store(id="rebalance-config-store"),
            dcc.Store(id="column-visibility-store", data=DEFAULT_VISIBLE_COLS),
            # ── Row 1: KPI Summary (always portfolio-scoped) ──────────
            dbc.Row(
                [
                    dcc.Loading(
                        type="dot",
                        children=dbc.Col(
                            id="portfolio_kpi_container",
                            children=kpi_row(),
                        ),
                    )
                ],
                className="mb-0",
            ),
            # ── Row 2: Filter Controls ────────────────────────────────
            workspace_filter_bar(),
            workspace_advanced_filter(),
            column_visibility_popover(),
            # ── Row 3: Analysis Workspace + Rebalance Drawer ──────────
            html.Div(
                [
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
                                        id="workspace-table-statusbar",
                                        className="workspace-table-statusbar",
                                        children="Loading assets…",
                                    ),
                                    html.Div(
                                        id="portfolio_page_asset_table_container",
                                        children=asset_table(None),
                                        style={
                                            "flex": "1",
                                            "minHeight": "0",
                                            "overflow": "hidden",
                                        },
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
                                        children=html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.Span(
                                                            id="assign-tag-modal-title",
                                                            className="ws-modal-title",
                                                        ),
                                                        html.Button(
                                                            "×",
                                                            id="assign-tag-modal-close-btn",
                                                            className="ws-modal-close",
                                                        ),
                                                    ],
                                                    className="ws-modal-header",
                                                ),
                                                html.Div(
                                                    [
                                                        html.Div(
                                                            [
                                                                html.Label(
                                                                    "Tag",
                                                                    className="ws-modal-label",
                                                                ),
                                                                tv_dropdown(
                                                                    id="assign-tag-modal-tag-select",
                                                                    placeholder="Select tag…",
                                                                    className="ws-modal-dropdown",
                                                                ),
                                                            ],
                                                            className="mb-3",
                                                        ),
                                                        html.Div(
                                                            [
                                                                html.Label(
                                                                    "Category",
                                                                    className="ws-modal-label",
                                                                ),
                                                                tv_dropdown(
                                                                    id="assign-tag-modal-category-select",
                                                                    placeholder="Select category…",
                                                                    className="ws-modal-dropdown",
                                                                ),
                                                            ],
                                                            className="mb-3",
                                                        ),
                                                    ],
                                                    className="ws-modal-body",
                                                ),
                                                html.Div(
                                                    [
                                                        dbc.Button(
                                                            "Save",
                                                            id="assign-tag-modal-save-btn",
                                                            color="primary",
                                                            size="sm",
                                                        ),
                                                        html.Small(
                                                            "",
                                                            id="assign-tag-modal-status",
                                                            className="text-muted ms-3",
                                                        ),
                                                    ],
                                                    className="ws-modal-footer",
                                                ),
                                            ],
                                            className="ws-modal-card",
                                        ),
                                    ),
                                ],
                            ),
                        ],
                    ),
                    # Rebalance config drawer (hidden by default, shown via toggle, RIGHT side)
                    html.Div(
                        id="rebalance-panel-wrapper",
                        className="rebalance-drawer",
                        style={"display": "none"},
                        children=rebalance_drawer_content(),
                    ),
                ],
                className="workspace-with-rebalance",
            ),
        ],
        id="portfolio-page-root",
    )
