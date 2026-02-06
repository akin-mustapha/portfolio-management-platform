import os
import httpx
import base64
import logging
from urllib.parse import urljoin

os.path.exists('logs') or os.makedirs('logs')
log_dir_name = 'logs'

logging.basicConfig(level=logging.INFO, filename=f'{log_dir_name}/info.log', filemode='w', format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')

class Trading212APIClient:
    def __init__(self, url: str, api_token: str, secret_token: str):
        self.url = url
        self.api_token = api_token
        self.secret_token = secret_token

    def credentials(self) -> str:
        credentials = f"{self.api_token}:{self.secret_token}"
        token = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

        logging.info(token)
        return token

    async def get(self, endpoint: str) -> dict:
        header = {"Authorization": f'Basic {self.credentials()}'}
        async with httpx.AsyncClient() as client:
            url = urljoin(self.url, endpoint)

            logging.info(f"Making API call to {url}")

            response = await client.get(url, headers=header)
            if response.status_code == 200:
                logging.info("Successful API call")
                return response.json()
            else:
                logging.error(f"API call failed with status code {response.status_code}")
                return {"error": response.status_code, "message": "API call failed"}