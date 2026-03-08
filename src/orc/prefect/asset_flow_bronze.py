import logging
from prefect import flow, task
from prefect.logging import loggers
from datetime import timedelta
from prefect.cache_policies import NO_CACHE
from ingestion.factories.pipeline_factory import PipelineFactory

from shared.utils.custom_logger import customer_logger

logger = loggers.get_logger(__name__)

@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_asset_bronze_pipeline():
    pipeline = PipelineFactory.get("asset_bronze")
    logger.info("Running Pipeline")
    pipeline.run()

@flow
def flow_t212_asset_bronze():
    logger.info("Starting the flow to fetch account cash")
    logger.info("Starting data ingestion process")
    task_asset_bronze_pipeline()
    logger.info("End data ingestion process")

    
if __name__ == "__main__": 
    flow_t212_asset_bronze.serve(
        name="t212_asset_bronze", interval=timedelta(seconds=600))  # Runs every 5mins