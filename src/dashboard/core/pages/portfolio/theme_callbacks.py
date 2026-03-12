from dash import Output, Input, State, callback, clientside_callback, Patch


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
# Note: "pnl_char" is the exact (typo'd) id used in the existing chart code

@callback(
    Output("winners_chart", "figure"),
    Output("losers_chart", "figure"),
    Output("value_chart", "figure"),
    Output("pnl_char", "figure"),
    Input("theme-store", "data"),
    prevent_initial_call=True,
)
def update_chart_theme(theme):
    is_dark = theme == "dark"
    bg     = "#1e222d" if is_dark else "white"
    fc     = "#9598a1" if is_dark else "#555555"
    rs_bg  = "#252d3d" if is_dark else "white"
    rs_ac  = "#1c2a4a" if is_dark else "#f0f0f0"

    def bar_patch():
        p = Patch()
        p["layout"]["paper_bgcolor"] = bg
        p["layout"]["plot_bgcolor"]  = bg
        p["layout"]["font"]["color"] = fc
        return p

    def line_patch():
        p = Patch()
        p["layout"]["paper_bgcolor"] = bg
        p["layout"]["plot_bgcolor"]  = bg
        p["layout"]["font"]["color"] = fc
        p["layout"]["xaxis"]["rangeselector"]["bgcolor"]     = rs_bg
        p["layout"]["xaxis"]["rangeselector"]["activecolor"] = rs_ac
        return p

    return bar_patch(), bar_patch(), line_patch(), line_patch()


# ── Patch workspace (asset) chart backgrounds on theme change ────────────────

@callback(
    Output("workspace-price-graph", "figure"),
    Output("workspace-value-graph", "figure"),
    Output("workspace-risk-graph", "figure"),
    Output("workspace-dca-graph", "figure"),
    Input("theme-store", "data"),
    prevent_initial_call=True,
)
def update_workspace_chart_theme(theme):
    is_dark = theme == "dark"
    bg    = "#1e222d" if is_dark else "white"
    fc    = "#9598a1" if is_dark else "#555555"
    rs_bg = "#252d3d" if is_dark else "white"
    rs_ac = "#1c2a4a" if is_dark else "#f0f0f0"

    def line_patch():
        p = Patch()
        p["layout"]["paper_bgcolor"] = bg
        p["layout"]["plot_bgcolor"]  = bg
        p["layout"]["font"]["color"] = fc
        p["layout"]["xaxis"]["rangeselector"]["bgcolor"]     = rs_bg
        p["layout"]["xaxis"]["rangeselector"]["activecolor"] = rs_ac
        return p

    return line_patch(), line_patch(), line_patch(), line_patch()


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
