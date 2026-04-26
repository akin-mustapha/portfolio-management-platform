import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from shared.database.client import SQLModelClient
from shared.database.query_loader import load_query

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

_QUERIES_DIR = Path(__file__).parent.parent.parent / "infrastructure" / "queries"

logging.basicConfig(
    level=logging.INFO,
    filename="logs/info.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
)


def _run_sync(query_file: str, target: str, source: str) -> None:
    sql = load_query(_QUERIES_DIR / "portfolio" / query_file).format(target=target, source=source)
    with SQLModelClient(database_url=DATABASE_URL or "") as client:
        client.execute(sql)


# Todo - dry up the individual synchronizer functions by passing in the query file, target and source as parameters. This will make it easier to add new synchronizers in the future without having to write a new function for each one.
def sychronize_industry():
    _run_sync("sync_industry.sql", target="staging.industry", source="portfolio.industry")


def sychronize_sector():
    _run_sync("sync_sector.sql", target="staging.sector", source="portfolio.sector")


def sychronize_tag():
    _run_sync("sync_tag.sql", target="staging.tag", source="portfolio.tag")


def sychronize_category():
    _run_sync("sync_category.sql", target="staging.category", source="portfolio.category")


def sychronize_asset_tag():
    _run_sync("sync_asset_tag.sql", target="staging.asset_tag", source="portfolio.asset_tag")


def enrichment_sychronization():
    logging.info("Sychronizing Industry")
    sychronize_industry()

    logging.info("Sychronizing Sector")

    sychronize_sector()

    logging.info("Sychronizing Tag")
    sychronize_tag()

    logging.info("Sychronizing Category")
    sychronize_category()

    logging.info("Sychronizing Asset Tag")
    sychronize_asset_tag()
