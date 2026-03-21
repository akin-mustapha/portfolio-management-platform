import logging
from prefect import flow, task
from prefect.cache_policies import NO_CACHE
from backend.ingestion.factories.pipeline_factory import PipelineFactory

from shared.utils.custom_logger import customer_logger

logging = customer_logger("asset_snapshot_flow_run")

@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_asset_portfolio_sync():
    pipeline = PipelineFactory.get("asset_portfolio")
    pipeline.run()

@flow
def flow_t212_asset_portfolio_sync():
    logging.info("Starting the flow to fetch account cash")
    logging.info("Starting data ingestion process")
    task_asset_portfolio_sync()
    logging.info("End data ingestion process")

