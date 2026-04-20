import os
import asyncio
import time
import httpx
import base64
import logging
from typing import Callable, Iterator, Optional
from urllib.parse import urljoin

from ...application.interfaces.interface_api_client import APIClient

os.path.exists("logs") or os.makedirs("logs")
log_dir_name = "logs"

logging.basicConfig(
    level=logging.INFO,
    filename=f"{log_dir_name}/info.log",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
)


class Trading212APIClient(APIClient):
    def __init__(self, url: str, api_token: str, secret_token: str):
        self.url = url
        self.api_token = api_token
        self.secret_token = secret_token

    def credentials(self) -> str:
        credentials = f"{self.api_token}:{self.secret_token}"
        token = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

        logging.info(token)
        return token

    async def get(self, endpoint: str) -> dict:
        header = {"Authorization": f"Basic {self.credentials()}"}
        async with httpx.AsyncClient() as client:
            url = urljoin(self.url, endpoint)

            logging.info(f"Making API call to {url}")

            response = await client.get(url, headers=header)
            if response.status_code == 200:
                logging.info("Successful API call")
                return response.json()
            else:
                logging.error(
                    f"API call failed with status code {response.status_code}"
                )
                return {"error": response.status_code, "message": "API call failed"}

    def iter_paginated(
        self,
        endpoint: str,
        cursor: Optional[str] = None,
        limit: int = 50,
        stop_predicate: Optional[Callable[[dict], bool]] = None,
    ) -> Iterator[dict]:
        """
        Synchronous page iterator for T212 cursor-paginated endpoints.

        Follows nextPagePath until exhausted or stop_predicate(page) returns True.
        On HTTP 429, reads x-ratelimit-reset and sleeps with time.sleep (safe in
        Prefect sync tasks — no async event loop interference).
        On other non-200, raises httpx.HTTPStatusError.
        """
        header = {"Authorization": f"Basic {self.credentials()}"}

        next_path = f"{endpoint}?limit={limit}"
        if cursor is not None:
            next_path = f"{next_path}&cursor={cursor}"

        with httpx.Client() as client:
            while next_path:
                url = urljoin(self.url, next_path)
                logging.info(f"Paginated API call to {url}")
                response = client.get(url, headers=header)

                if response.status_code == 429:
                    reset = response.headers.get("x-ratelimit-reset")
                    wait_s = max(int(reset) - int(time.time()), 1) if reset else 5
                    logging.warning(f"Rate limited; sleeping {wait_s}s")
                    time.sleep(wait_s)
                    continue

                response.raise_for_status()
                page = response.json()

                yield page

                if stop_predicate is not None and stop_predicate(page):
                    return

                next_path = page.get("nextPagePath")
