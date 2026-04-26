"""
Asset Portfolio Pipeline

Sync asset list from silver asset store to OLTP portfolio asset table

Source -> Destination (no transformation)
"""

import logging
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from dotenv import load_dotenv
from shared.database.client import SQLModelClient
from shared.database.query_loader import load_query

from pipeline.etl.policies import Pipeline
from pipeline.etl.protocols import Destination, Source

logging.basicConfig(
    level=logging.INFO,
    filename="logs/info.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

_QUERIES_DIR = Path(__file__).parent.parent.parent / "infrastructure" / "queries"


@dataclass
class Asset:
    ticker: str
    name: str
    broker: str
    currency: str


class AssetPortfolioSource(Source):
    def __init__(self):
        self._sql = load_query(_QUERIES_DIR / "portfolio" / "asset_portfolio_source.sql")

    def extract(self) -> list:
        with SQLModelClient(DATABASE_URL or "") as client:
            return client.execute(self._sql)


class AssetPortfolioDestination(Destination):
    def __init__(self):
        self._template = load_query(_QUERIES_DIR / "portfolio" / "asset_portfolio_upsert.sql")

    def load(self, data: list[dict]) -> None:
        # INSERTION POLICY: IDEMPOTENT
        merge_value_mapping = ",".join(
            [
                f"""(
            '{r.get("ticker")}'
          , '{r.get("name")}'
          , '{r.get("broker")}'
          , '{r.get("currency")}'
          )
        """
                for r in data
            ]
        )

        asset_upsert_sql = self._template.format(
            destination_table_name="portfolio.asset",
            values=merge_value_mapping,
        )

        with SQLModelClient(DATABASE_URL or "") as client:
            client.execute(asset_upsert_sql)


class PipelineAssetPortfolio(Pipeline):
    def __init__(self):
        self._source = AssetPortfolioSource()
        self._destination = AssetPortfolioDestination()

    def run(self):
        try:
            data = self._source.extract()

            # DESTINATION Schema Contract
            # Dataclass creates a boundary between source and destination physical storage
            data = [
                asdict(
                    Asset(
                        ticker=row._mapping.get("ticker"),
                        name=row._mapping.get("name"),
                        broker=row._mapping.get("broker"),
                        currency=row._mapping.get("currency"),
                    )
                )
                for row in data
            ]

            self._destination.load(data)
            return None

        except Exception as e:
            raise e


if __name__ == "__main__":
    PipelineAssetPortfolio().run()
