from flask import Blueprint, jsonify, request
from backend.infrastructure.credentials.repository import CredentialsRepository

credentials_bp = Blueprint("credentials", __name__)

PROVIDER = "trading212"


@credentials_bp.route("/api/credentials", methods=["GET"])
def get_credentials():
    """Return stored API key and URL for the provider."""
    try:
        repo = CredentialsRepository()
        row = repo.load(PROVIDER)
        if row:
            return jsonify(
                {
                    "api_key": row.get("api_key", ""),
                    "secret_token": row.get("secret_token", ""),
                    "api_url": row.get("api_url", ""),
                }
            )
        return jsonify({"api_key": "", "api_url": ""})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@credentials_bp.route("/api/credentials", methods=["POST"])
def save_credentials():
    """Save API key and URL for the provider."""
    data = request.get_json(silent=True) or {}
    api_key = (data.get("api_key") or "").strip()
    secret_token = (data.get("secret_token") or "").strip()
    api_url = (data.get("api_url") or "").strip()

    if not api_key:
        return jsonify({"error": "api_key is required"}), 400

    try:
        repo = CredentialsRepository()
        repo.save(PROVIDER, api_key, secret_token, api_url)
        return jsonify({"status": "saved"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
