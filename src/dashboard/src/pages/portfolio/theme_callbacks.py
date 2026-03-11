from dash import Output, Input, State, callback, clientside_callback, Patch


# ── Privacy toggle ───────────────────────────────────────────────────────────

# 1. Toggle privacy-store on button click
@callback(
    Output("privacy-store", "data"),
    Input("privacy-toggle-btn", "n_clicks"),
    State("privacy-store", "data"),
    prevent_initial_call=True,
)
def toggle_privacy(n_clicks, current):
    return not bool(current)


# 2. Swap eye icon and highlight button blue when privacy is on (clientside)
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


# 1. Toggle theme store value on button click
@callback(
    Output("theme-store", "data"),
    Input("theme-toggle-btn", "n_clicks"),
    State("theme-store", "data"),
    prevent_initial_call=True,
)
def toggle_theme(n_clicks, current_theme):
    return "dark" if current_theme == "light" else "light"


# 2. Apply data-theme to <html> and swap moon/sun icon (clientside — DOM access required)
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


# 3. Patch Plotly chart backgrounds on theme change (no data refetch)
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


# 4. Patch asset page chart backgrounds on theme change
@callback(
    Output("price_graph", "figure"),
    Output("value_graph", "figure"),
    Output("risk_graph", "figure"),
    Output("dca_graph", "figure"),
    Input("theme-store", "data"),
    prevent_initial_call=True,
)
def update_asset_chart_theme(theme):
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
