"""
  CSS Style as Python Dict
"""
# sidebar + content styles
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "4rem 1rem 1rem 1rem",
    "transition": "all 0.3s",
    # "overflow": "hidden",
}

SIDEBAR_HIDDEN = SIDEBAR_STYLE.copy()
SIDEBAR_HIDDEN["width"] = "0rem"
SIDEBAR_HIDDEN["padding"] = "4rem 0 0 0"
SIDEBAR_HIDDEN["visibility"] = "hidden"

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
    "transition": "margin-left 0.3s",
}

CONTENT_STYLE_EXPANDED = CONTENT_STYLE.copy()
CONTENT_STYLE_EXPANDED["margin-left"] = "0rem"


TAB_CONTENT_STYLE = {
  "padding": "2rem 1rem",
  "height": 800
}