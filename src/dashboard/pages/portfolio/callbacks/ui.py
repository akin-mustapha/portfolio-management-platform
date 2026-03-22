"""
UI toggle callbacks — collapse panels in the filter bar and each tab.
These have no data dependency; they only flip is_open state.
"""
from dash import Output, Input, State, callback


# ── 5. Advanced filter collapse ───────────────────────────────────

@callback(
    Output("workspace-adv-filter-collapse", "is_open"),
    Input("workspace-adv-filter-btn", "n_clicks"),
    State("workspace-adv-filter-collapse", "is_open"),
    prevent_initial_call=True,
)
def toggle_advanced_filter(n, is_open):
    return not is_open if n else is_open


# ── 5a. Valuation tab — portfolio section collapse ────────────────

@callback(
    Output("portfolio-charts-collapse", "is_open"),
    Input("portfolio-section-header",   "n_clicks"),
    State("portfolio-charts-collapse",  "is_open"),
    prevent_initial_call=True,
)
def toggle_portfolio_section(n, is_open):
    return not is_open if n else is_open


# ── 5c. Risk tab — portfolio section collapse ─────────────────────

@callback(
    Output("risk-portfolio-charts-collapse", "is_open"),
    Input("risk-portfolio-section-header",   "n_clicks"),
    State("risk-portfolio-charts-collapse",  "is_open"),
    prevent_initial_call=True,
)
def toggle_risk_portfolio_section(n, is_open):
    return not is_open if n else is_open


# ── 5e. Opportunities tab — portfolio section collapse ────────────

@callback(
    Output("opportunities-portfolio-charts-collapse", "is_open"),
    Input("opportunities-portfolio-section-header",   "n_clicks"),
    State("opportunities-portfolio-charts-collapse",  "is_open"),
    prevent_initial_call=True,
)
def toggle_opportunities_portfolio_section(n, is_open):
    return not is_open if n else is_open
