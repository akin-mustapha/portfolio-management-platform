from dash import Input, Output, State, callback, clientside_callback


# Open / close the settings modal
@callback(
    Output("settings-modal", "is_open"),
    Input("settings-btn", "n_clicks"),
    State("settings-modal", "is_open"),
    prevent_initial_call=True,
)
def toggle_settings_modal(n_clicks, is_open):
    return not is_open


# Populate inputs from store when modal opens
@callback(
    Output("settings-api-key-input", "value"),
    Output("settings-api-url-input", "value"),
    Input("settings-modal", "is_open"),
    State("api-key-store", "data"),
    State("api-url-store", "data"),
    prevent_initial_call=True,
)
def load_stored_credentials(is_open, stored_key, stored_url):
    if is_open:
        return stored_key or "", stored_url or ""
    return "", ""


# Save credentials to store
@callback(
    Output("api-key-store", "data"),
    Output("api-url-store", "data"),
    Output("settings-save-status", "children"),
    Input("settings-save-btn", "n_clicks"),
    State("settings-api-key-input", "value"),
    State("settings-api-url-input", "value"),
    prevent_initial_call=True,
)
def save_credentials(n_clicks, key_value, url_value):
    if not key_value or not key_value.strip():
        return "", url_value or "", "Key cannot be empty."
    return key_value.strip(), (url_value or "").strip(), "Saved."


# Connect — test credentials and update status indicator
@callback(
    Output("settings-status-dot", "className"),
    Output("settings-status-label", "children"),
    Input("settings-connect-btn", "n_clicks"),
    State("settings-api-key-input", "value"),
    State("settings-api-url-input", "value"),
    prevent_initial_call=True,
)
def test_connection(n_clicks, key_value, url_value):
    if not key_value or not key_value.strip():
        return "settings-status-dot settings-status-dot--disconnected", "No key provided"
    try:
        import requests
        base = (url_value or "https://live.trading212.com").rstrip("/")
        resp = requests.get(
            f"{base}/api/v0/portfolio",
            headers={"Authorization": key_value.strip()},
            timeout=5,
        )
        if resp.status_code == 200:
            return "settings-status-dot settings-status-dot--connected", "Connected"
        return "settings-status-dot settings-status-dot--disconnected", f"Error {resp.status_code}"
    except Exception:
        return "settings-status-dot settings-status-dot--disconnected", "Connection failed"


# Toggle show/hide on the password input
clientside_callback(
    """
    function(n_clicks, current_type) {
        if (!n_clicks) return [window.dash_clientside.no_update, window.dash_clientside.no_update];
        var show = current_type === 'password';
        return [
            show ? 'text' : 'password',
            show ? 'fa-solid fa-eye-slash' : 'fa-solid fa-eye'
        ];
    }
    """,
    Output("settings-api-key-input", "type"),
    Output("settings-key-eye-icon", "className"),
    Input("settings-key-eye-btn", "n_clicks"),
    State("settings-api-key-input", "type"),
    prevent_initial_call=True,
)
