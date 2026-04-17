import logging
import httpx
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    filename="logs/info.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
)

# TODO: move to config
BASE_URL = "https://api.stlouisfed.org/fred/"


class FredAPIClient:
    def __init__(self, api_key: str):
        self._api_key = api_key

    def get_observations(self, series_id: str, observation_start: str) -> dict:
        """
        Fetch observations for a FRED series.

        Args:
            series_id: e.g. 'DTB3' or 'SP500'
            observation_start: ISO date string 'YYYY-MM-DD'

        Returns:
            Raw JSON dict from FRED: {"observations": [{date, value}, ...], ...}

        Raises:
            httpx.HTTPStatusError on non-2xx responses.
        """
        params = {
            "series_id": series_id,
            "observation_start": observation_start,
            "file_type": "json",
            "api_key": self._api_key,
        }
        logging.info(f"Fetching FRED series {series_id} from {observation_start}")
        with httpx.Client() as client:
            response = client.get(
                f"{BASE_URL}series/observations",
                params=params,
                timeout=30.0,
            )
        response.raise_for_status()
        logging.info(
            f"FRED series {series_id}: {len(response.json().get('observations', []))} observations"
        )
        return response.json()
