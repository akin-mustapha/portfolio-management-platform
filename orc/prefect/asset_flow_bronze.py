import logging
from prefect import flow, task
from datetime import timedelta
from prefect.cache_policies import NO_CACHE
from src.services.ingestion.pipeline_factory import PipelineFactory

from src.shared.utils.custom_logger import customer_logger

logging = customer_logger("asset_flow_run")

@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_asset_bronze_pipeline():
    pipeline = PipelineFactory.get("bronze_asset")
    pipeline.run()

@flow
def flow_t212_asset_bronze():
    logging.info("Starting the flow to fetch account cash")
    logging.info("Starting data ingestion process")
    task_asset_bronze_pipeline()
    logging.info("End data ingestion process")

    
if __name__ == "__main__": 
    flow_t212_asset_bronze.serve(
        name="t212_asset_bronze", interval=timedelta(seconds=600))  # Runs every 5mins