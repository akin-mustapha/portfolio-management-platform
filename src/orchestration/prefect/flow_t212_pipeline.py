import os
from dotenv import load_dotenv
from prefect import flow, task
from prefect.logging import loggers
from prefect.cache_policies import NO_CACHE

from backend.ingestion.factories.pipeline_factory import PipelineFactory
from shared.database.client import SQLModelClient

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

logger = loggers.get_logger(__name__)


@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_bronze():
    pipeline = PipelineFactory.get("t212_bronze")
    logger.info("Running unified bronze pipeline")
    pipeline.run()


@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_silver():
    pipeline = PipelineFactory.get("t212_silver")
    logger.info("Running unified silver pipeline")
    pipeline.run()


@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_asset_computed_silver():
    pipeline = PipelineFactory.get("asset_computed_silver")
    logger.info("Running asset computed silver pipeline")
    pipeline.run()


@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_account_computed_silver():
    pipeline = PipelineFactory.get("account_computed_silver")
    logger.info("Running account computed silver pipeline")
    pipeline.run()


@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_asset_gold():
    pipeline = PipelineFactory.get("asset_gold")
    logger.info("Running asset gold pipeline")
    pipeline.run()


@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_account_gold():
    pipeline = PipelineFactory.get("account_gold")
    logger.info("Running account gold pipeline")
    pipeline.run()


@task(cache_policy=NO_CACHE)
def task_mark_snapshot_processed():
    sql = "UPDATE raw.t212_snapshot SET processed_at = now() WHERE processed_at IS NULL"
    with SQLModelClient(DATABASE_URL) as client:
        client.execute(sql)
    logger.info("Marked unprocessed snapshots as processed")


@flow
def flow_t212_pipeline():
    logger.info("Starting pipeline: bronze → silver → computed silver → gold")

    task_bronze()

    task_silver()

    task_asset_computed_silver()
    task_account_computed_silver()

    task_asset_gold()
    task_account_gold()

    task_mark_snapshot_processed()

    logger.info("Pipeline complete")
