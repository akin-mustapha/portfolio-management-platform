import dash_bootstrap_components as dbc
# toggle button outside sidebar
btn_side_toggle = dbc.Button("☰", id="sidebar-toggle",color="primary",
                        style={"position": "fixed", "top": "1rem", "left": "1rem", "zIndex": 999})
