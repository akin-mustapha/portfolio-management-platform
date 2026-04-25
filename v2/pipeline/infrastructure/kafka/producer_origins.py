import os
import asyncio
from dotenv import load_dotenv

from pipeline.etl.policies import Origin

# TODO: should depend on interface
from pipeline.infrastructure.clients.api_client_trading212 import Trading212APIClient

load_dotenv()


# Try to load credentials from DB (set via Settings modal).
# Fall back to .env so existing pipeline runs keep working if no DB row exists yet.
def _load_credentials():
    try:
        from backend.infrastructure.credentials.repository import CredentialsRepository

        row = CredentialsRepository().load("trading212")
        if row and row.get("api_key"):
            return (
                row.get("api_url") or os.getenv("API_URL"),
                row["api_key"],
                row.get("secret_token") or os.getenv("SECRET_TOKEN"),
            )
    except Exception:
        pass
    return os.getenv("API_URL"), os.getenv("API_TOKEN"), os.getenv("SECRET_TOKEN")


URL, API_TOKEN, SECRET_TOKEN = _load_credentials()


class Trading212AssetAPIOrigin(Origin):
    def __init__(self, origin_name: str):
        super().__init__(origin_name)
        self._url = URL
        self._endpoint = "equity/positions"
        self._api_token = API_TOKEN
        self._secret_token = SECRET_TOKEN
        self._api_client = Trading212APIClient(
            self._url, self._api_token, self._secret_token
        )

    def _handler(self):
        data = asyncio.run(self._api_client.get(endpoint=self._endpoint))
        self._metadata = {
            "url": self._url,
            "endpoint": self._endpoint,
            "origin": self.origin_name,
        }
        return data
