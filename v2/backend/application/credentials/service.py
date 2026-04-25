from backend.infrastructure.credentials.repository import CredentialsRepository


class CredentialsService:
    def __init__(self, repo: CredentialsRepository):
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
        api_key = api_key.strip()
        if not api_key:
            raise ValueError("api_key is required")
        self._repo.save(provider, api_key, secret_token.strip(), api_url.strip())


def build_credentials_service() -> CredentialsService:
    return CredentialsService(CredentialsRepository())
