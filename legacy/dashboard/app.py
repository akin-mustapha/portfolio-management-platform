import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_VAULT = _ROOT / "vault"
for _p in (str(_ROOT), str(_VAULT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from dash import Dash
import dash_bootstrap_components as dbc
from .layouts.layout import layout
from .api.credentials_routes import credentials_bp

plotly_config = {
    "staticPlot": True,
    "scrollZoom": True,
    "displayModeBar": False,
    "editable": True,
}


# App
app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.COSMO,
        dbc.icons.FONT_AWESOME,
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ],
)

app.layout = layout
app.server.register_blueprint(credentials_bp)

# Anti-FOUC: read stored theme from localStorage and apply before first paint
app.index_string = """<!DOCTYPE html>
<html>
<head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    {%css%}
    <script>
        (function() {
            try {
                var raw = localStorage.getItem('theme-store');
                if (raw) {
                    var theme = JSON.parse(raw);
                    if (typeof theme === 'string' && (theme === 'dark' || theme === 'light')) {
                        document.documentElement.setAttribute('data-theme', theme);
                    }
                }
            } catch(e) {}
        })();
    </script>
</head>
<body>
    {%app_entry%}
    <footer>
        {%config%}
        {%scripts%}
        {%renderer%}
    </footer>
</body>
</html>"""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False, dev_tools_ui=True)
