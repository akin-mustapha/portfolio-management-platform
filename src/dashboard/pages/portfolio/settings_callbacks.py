import base64
import requests as http
from urllib.parse import urljoin
from dash import Input, Output, State, callback, clientside_callback, no_update


# Open / close the settings modal
@callback(
    Output("settings-modal", "is_open"),
    Input("settings-btn", "n_clicks"),
    State("settings-modal", "is_open"),
    prevent_initial_call=True,
)
def toggle_settings_modal(n_clicks, is_open):
    return not is_open


# Populate inputs from DB when modal opens; sync stores so other callbacks have fast access
@callback(
    Output("settings-api-key-input", "value"),
    Output("settings-secret-token-input", "value"),
    Output("settings-api-url-input", "value"),
    Output("api-key-store", "data"),
    Output("api-url-store", "data"),
    Input("settings-modal", "is_open"),
    prevent_initial_call=True,
)
def load_stored_credentials(is_open):
    if not is_open:
        return no_update, no_update, no_update, no_update, no_update
    try:
        resp = http.get("http://localhost:8050/api/credentials", timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            key = data.get("api_key", "")
            secret = data.get("secret_token", "")
            url = data.get("api_url", "")
            return key, secret, url, key, url
    except Exception:
        pass
    return "", "", "", "", ""


# Save credentials to DB (and keep stores in sync)
@callback(
    Output("api-key-store", "data", allow_duplicate=True),
    Output("api-url-store", "data", allow_duplicate=True),
    Output("settings-save-status", "children"),
    Input("settings-save-btn", "n_clicks"),
    State("settings-api-key-input", "value"),
    State("settings-secret-token-input", "value"),
    State("settings-api-url-input", "value"),
    prevent_initial_call=True,
)
def save_credentials(n_clicks, key_value, secret_value, url_value):
    if not key_value or not key_value.strip():
        return no_update, no_update, "Key cannot be empty."
    try:
        resp = http.post(
            "http://localhost:8050/api/credentials",
            json={
                "api_key": key_value.strip(),
                "secret_token": (secret_value or "").strip(),
                "api_url": (url_value or "").strip(),
            },
            timeout=3,
        )
        if resp.status_code == 200:
            return key_value.strip(), (url_value or "").strip(), "Saved."
        return no_update, no_update, f"Error: {resp.status_code}"
    except Exception as e:
        return no_update, no_update, f"Failed: {e}"


# Connect — test credentials using the same Basic Auth as the pipeline, before saving
@callback(
    Output("settings-status-dot", "className"),
    Output("settings-status-label", "children"),
    Input("settings-connect-btn", "n_clicks"),
    State("settings-api-key-input", "value"),
    State("settings-secret-token-input", "value"),
    State("settings-api-url-input", "value"),
    prevent_initial_call=True,
)
def test_connection(n_clicks, key_value, secret_value, url_value):
    if not key_value or not key_value.strip():
        return "settings-status-dot settings-status-dot--disconnected", "No key provided"
    try:
        raw = f"{key_value.strip()}:{(secret_value or '').strip()}"
        token = base64.b64encode(raw.encode()).decode()
        base_url = (url_value or "").rstrip("/") or "https://live.trading212.com"
        url = urljoin(base_url + "/", "equity/positions")
        resp = http.get(
            url,
            headers={"Authorization": f"Basic {token}"},
            timeout=5,
        )
        if resp.status_code == 200:
            return "settings-status-dot settings-status-dot--connected", "Connected"
        return "settings-status-dot settings-status-dot--disconnected", f"Error {resp.status_code}"
    except Exception:
        return "settings-status-dot settings-status-dot--disconnected", "Connection failed"


# Toggle show/hide on the API key input
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

# Toggle show/hide on the secret token input
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
    Output("settings-secret-token-input", "type"),
    Output("settings-secret-eye-icon", "className"),
    Input("settings-secret-eye-btn", "n_clicks"),
    State("settings-secret-token-input", "type"),
    prevent_initial_call=True,
)
