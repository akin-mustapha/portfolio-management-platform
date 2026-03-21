from dash import Output, Input, State, callback, clientside_callback, no_update, Patch

from .callbacks import (
    _build_compare_rows,
    _date_window,
    _fetch_snapshots,
    _VALUATION_METRICS,
    _RISK_METRICS,
    _OPPS_METRICS,
)


# ── Privacy toggle ───────────────────────────────────────────────────────────

@callback(
    Output("privacy-store", "data"),
    Input("privacy-toggle-btn", "n_clicks"),
    State("privacy-store", "data"),
    prevent_initial_call=True,
)
def toggle_privacy(n_clicks, current):
    return not bool(current)


clientside_callback(
    """
    function(privacy) {
        var on = privacy === true;
        document.documentElement.setAttribute('data-privacy', on ? 'true' : 'false');
        var btn = document.getElementById('privacy-toggle-btn');
        if (btn) btn.style.color = on ? 'var(--bs-primary, #0d6efd)' : '';
        return on ? 'fa-solid fa-eye-slash' : 'fa-solid fa-eye';
    }
    """,
    Output("privacy-toggle-icon", "className"),
    Input("privacy-store", "data"),
)


# ── Theme toggle ─────────────────────────────────────────────────────────────

@callback(
    Output("theme-store", "data"),
    Input("theme-toggle-btn", "n_clicks"),
    State("theme-store", "data"),
    prevent_initial_call=True,
)
def toggle_theme(n_clicks, current_theme):
    return "dark" if current_theme == "light" else "light"


clientside_callback(
    """
    function(theme) {
        var t = theme || 'light';
        document.documentElement.setAttribute('data-theme', t);
        return t === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
    }
    """,
    Output("theme-toggle-icon", "className"),
    Input("theme-store", "data"),
)


# ── Patch portfolio chart backgrounds on theme change ────────────────────────

@callback(
    Output("value_chart", "figure"),
    Output("pnl_chart", "figure"),
    Output("losers_pnl_chart", "figure"),
    Output("winners_pnl_chart", "figure"),
    Output("position_weight_donut_chart", "figure"),
    Output("profitability_donut_chart", "figure"),
    Output("portfolio_performance_map", "figure"),
    Output("portfolio_drawdown_chart", "figure"),
    Output("var_by_position_chart", "figure"),
    Input("theme-store", "data"),
    prevent_initial_call=True,
)
def update_chart_theme(theme):
    is_dark = theme == "dark"
    bg = "#1e222d" if is_dark else "white"
    fc = "#9598a1" if is_dark else "#555555"

    def patch():
        p = Patch()
        p["layout"]["paper_bgcolor"] = bg
        p["layout"]["plot_bgcolor"]  = bg
        p["layout"]["font"]["color"] = fc
        return p

    return (
        patch(), patch(),  # value_chart, pnl_chart
        patch(), patch(),  # losers_pnl_chart, winners_pnl_chart
        patch(), patch(),  # position_weight_donut_chart, profitability_donut_chart
        patch(),           # portfolio_performance_map
        patch(),           # portfolio_drawdown_chart
        patch(),           # var_by_position_chart
    )


# ── Rebuild workspace (asset) charts on theme change ─────────────────────────

@callback(
    Output("asset-detail-sections", "children", allow_duplicate=True),
    Output("risk-asset-detail-sections", "children", allow_duplicate=True),
    Output("opportunities-asset-detail-sections", "children", allow_duplicate=True),
    Input("theme-store", "data"),
    State("workspace-selected-asset", "data"),
    State("workspace-timeframe", "data"),
    State("portfolio_page_asset_store", "data"),
    prevent_initial_call=True,
)
def update_workspace_chart_theme(theme, selected_assets, timeframe, asset_store):
    tickers = selected_assets if isinstance(selected_assets, list) else []
    if not tickers:
        return no_update, no_update, no_update

    current_theme = theme or "light"
    start_date, end_date = _date_window(timeframe or "1Y")

    snapshots = _fetch_snapshots(tickers, start_date, end_date)
    asset_rows = (asset_store or {}).get("view_model", {}).get("asset_table", {}).get("rows", [])
    names_map = {r["ticker"]: r.get("name", "") for r in asset_rows if r.get("ticker")}

    return (
        _build_compare_rows(snapshots, _VALUATION_METRICS, current_theme, ns="val", names_map=names_map),
        _build_compare_rows(snapshots, _RISK_METRICS, current_theme, ns="risk", names_map=names_map),
        _build_compare_rows(snapshots, _OPPS_METRICS, current_theme, ns="opps", names_map=names_map),
    )


# ── Clientside: drag-to-resize split panel ───────────────────────────────────

clientside_callback(
    """
    function(_) {
        var divider = document.getElementById('split-divider');
        var left    = document.getElementById('workspace-left');
        var split   = document.getElementById('workspace-split');
        if (!divider || !left || !split) return window.dash_clientside.no_update;

        var isDragging = false;
        var startX = 0;
        var startWidth = 0;

        divider.addEventListener('mousedown', function(e) {
            isDragging = true;
            startX = e.clientX;
            startWidth = left.getBoundingClientRect().width;
            divider.classList.add('dragging');
            document.body.style.cursor = 'col-resize';
            document.body.style.userSelect = 'none';
            e.preventDefault();
        });

        document.addEventListener('mousemove', function(e) {
            if (!isDragging) return;
            var newWidth = startWidth + (e.clientX - startX);
            var minW = 280;
            var maxW = split.getBoundingClientRect().width * 0.6;
            newWidth = Math.max(minW, Math.min(newWidth, maxW));
            left.style.width = newWidth + 'px';
            left.style.flex  = 'none';
        });

        document.addEventListener('mouseup', function() {
            if (!isDragging) return;
            isDragging = false;
            divider.classList.remove('dragging');
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
        });

        return window.dash_clientside.no_update;
    }
    """,
    Output("workspace-split", "data-initialized"),
    Input("workspace-split", "id"),
)


# ── Clientside: ResizeObserver for responsive chart grid ────────────────────

clientside_callback(
    """
    function(_) {
        var rightPanel = document.getElementById('workspace-right');
        if (!rightPanel || typeof ResizeObserver === 'undefined')
            return window.dash_clientside.no_update;

        var observer = new ResizeObserver(function(entries) {
            for (var entry of entries) {
                var width = entry.contentRect.width;
                var grids = rightPanel.querySelectorAll('.workspace-chart-grid');
                grids.forEach(function(g) {
                    if (width < 600) {
                        g.classList.add('chart-grid-single');
                    } else {
                        g.classList.remove('chart-grid-single');
                    }
                });
            }
        });
        observer.observe(rightPanel);
        return window.dash_clientside.no_update;
    }
    """,
    Output("workspace-right", "data-observer"),
    Input("workspace-right", "id"),
)
