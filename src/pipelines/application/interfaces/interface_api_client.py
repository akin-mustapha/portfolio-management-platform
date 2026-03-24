from abc import ABC, abstractmethod


class APIClient(ABC):
    def __init__(self, url: str, api_token: str, secret_token: str):
        self.url = url
        self.api_token = api_token
        self.secret_token = secret_token

    @abstractmethod
    def credentials(self) -> str:
        pass

    @abstractmethod
    async def get(self, endpoint: str) -> dict:
        pass
