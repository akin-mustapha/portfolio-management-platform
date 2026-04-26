import os
from dotenv import load_dotenv
from prefect import flow, task
from prefect.logging import loggers
from prefect.cache_policies import NO_CACHE

from pipeline.infrastructure.factories.pipeline_factory import PipelineFactory
from shared.database.client import SQLModelClient

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

logger = loggers.get_logger(__name__)


@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_silver():
    pipeline = PipelineFactory.get("t212_silver")
    logger.info("Running unified silver pipeline")
    pipeline.run()


@task(cache_policy=NO_CACHE)
def task_mark_snapshot_processed():
    sql = "UPDATE raw.t212_snapshot SET processed_at = now() WHERE processed_at IS NULL"
    with SQLModelClient(DATABASE_URL) as client:
        client.execute(sql)
    logger.info("Marked unprocessed snapshots as processed")


@flow
def flow_t212_silver():
    logger.info("Starting silver pipeline")

    task_silver()

    task_mark_snapshot_processed()

    logger.info("Silver pipeline complete")


if __name__ == "__main__":
    flow_t212_silver()
