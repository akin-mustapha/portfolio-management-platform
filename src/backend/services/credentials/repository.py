from shared.repositories.base_table_repository import BaseTableRepository


class CredentialsRepository(BaseTableRepository):
    def __init__(self):
        super().__init__("api_credentials", schema_name="portfolio")

    def save(
        self, provider: str, api_key: str, secret_token: str = None, api_url: str = None
    ) -> None:
        """Upsert credentials for a provider. One row per provider."""
        self.upsert(
            [
                {
                    "provider": provider,
                    "api_key": api_key,
                    "secret_token": secret_token or "",
                    "api_url": api_url or "",
                }
            ],
            unique_key=["provider"],
        )

    def load(self, provider: str) -> dict | None:
        """Return {"api_key": ..., "api_url": ...} or None if not found."""
        return self.select({"provider": provider})
