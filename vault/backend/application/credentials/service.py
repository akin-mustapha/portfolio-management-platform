from backend.application.credentials.ports import CredentialsPort
from backend.domain.credentials.value_objects import ApiKey


class CredentialsService:
    def __init__(self, repo: CredentialsPort):
        self._repo = repo

    def get(self, provider: str) -> dict:
        row = self._repo.load(provider)
        if row:
            return {
                "api_key": row.get("api_key", ""),
                "secret_token": row.get("secret_token", ""),
                "api_url": row.get("api_url", ""),
            }
        return {"api_key": "", "secret_token": "", "api_url": ""}

    def save(self, provider: str, api_key: str, secret_token: str, api_url: str) -> None:
        validated_key = ApiKey(api_key)
        self._repo.save(provider, str(validated_key), secret_token.strip(), api_url.strip())
