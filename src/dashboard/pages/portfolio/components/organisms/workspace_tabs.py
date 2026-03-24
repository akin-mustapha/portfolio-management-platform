"""
Organism — workspace tab widget. Assembles the 4-tab panel.

Tab content lives in pages/portfolio/tabs/:
  tab_portfolio.py      → Valuation tab
  tab_risk.py           → Risk tab
  tab_opportunities.py  → Opportunities tab
  tab_asset_profile.py  → Asset Profile tab
"""

import dash_bootstrap_components as dbc

from ...tabs import (
    portfolio_tab_content,
    risk_tab_content,
    opportunities_tab_content,
    asset_profile_tab_content,
)


def workspace_tabs(view_model=None, theme="light"):
    """Renders the 4-tab workspace panel. Call on page load with portfolio view_model."""
    return dbc.Tabs(
        id="workspace-tabs",
        active_tab="tab-portfolio",
        className="workspace-tab-bar mb-0",
        children=[
            dbc.Tab(
                label="Valuation",
                tab_id="tab-portfolio",
                tab_class_name="workspace-tab",
                active_tab_class_name="workspace-tab--active",
                children=portfolio_tab_content(view_model, theme),
            ),
            dbc.Tab(
                label="Risk",
                tab_id="tab-risk",
                tab_class_name="workspace-tab",
                active_tab_class_name="workspace-tab--active",
                children=risk_tab_content(view_model, theme),
            ),
            dbc.Tab(
                label="Opportunities",
                tab_id="tab-opportunities",
                tab_class_name="workspace-tab",
                active_tab_class_name="workspace-tab--active",
                children=opportunities_tab_content(view_model, theme),
            ),
            dbc.Tab(
                label="Asset Profile",
                tab_id="tab-tags",
                tab_class_name="workspace-tab",
                active_tab_class_name="workspace-tab--active",
                children=asset_profile_tab_content(),
            ),
        ],
    )
