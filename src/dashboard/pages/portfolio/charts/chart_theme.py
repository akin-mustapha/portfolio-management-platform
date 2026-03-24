"""Chart color constants and theme definitions shared across all chart modules."""

# ── Sentiment colors ──────────────────────────────────────────────────────────

POSITIVE_COLOR = "#26a671"   # gain / positive — light mode
NEGATIVE_COLOR = "#ef5350"   # loss / negative — light mode
TEAL_COLOR     = "#26a69a"   # teal / neutral upside — light mode

# Semi-transparent fills used in chart shading
POSITIVE_FILL           = "rgba(38,166,113,0.18)"
NEGATIVE_FILL           = "rgba(239,83,80,0.18)"
TEAL_FILL               = "rgba(38,166,154,0.15)"
NEGATIVE_SPARKLINE_FILL = "rgba(239,83,80,0.15)"
MUTED_FILL              = "rgba(150,150,150,0.4)"

# Annotation / label colors
ANNOTATION_COLOR        = "gray"
MEDIAN_ANNOTATION_COLOR = "rgba(200,180,0,0.9)"
PIE_TEXT_COLOR          = "#ffffff"

# Fallback accent used when no accent_color is passed to a chart
FALLBACK_ACCENT = "#0d6efd"

# FX donut chart: light mode uses opaque primary, dark uses lighter variant
FX_CHART_COLORS = {
    "light": ["#0d6efd", "rgba(13,110,253,0.25)"],
    "dark":  ["#639aff", "rgba(99,154,255,0.25)"],
}

# ── Background / plot theme ───────────────────────────────────────────────────

CHART_THEMES = {
    "light": {
        "paper_bgcolor": "white",
        "plot_bgcolor": "white",
        "font_color": "#555555",
        "rs_bg": "white",
        "rs_active": "#f0f0f0",
    },
    "dark": {
        "paper_bgcolor": "#1e222d",
        "plot_bgcolor": "#1e222d",
        "font_color": "#9598a1",
        "rs_bg": "#252d3d",
        "rs_active": "#1c2a4a",
    },
}
