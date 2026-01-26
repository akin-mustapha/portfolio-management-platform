import logging
from prefect import flow, task
from datetime import timedelta
from prefect.cache_policies import NO_CACHE
from src.services.ingestion_service.application.pipelines. pipeline_factory import PipelineFactory

from src.shared.utils.custom_logger import customer_logger

logging = customer_logger("asset_flow_run")

@task(retry_delay_seconds=30, retries=2, cache_policy=NO_CACHE)
def task_run_asset_pipeline():
    pipeline = PipelineFactory.get("trading212AssetPipeline")
    pipeline.run()

@flow
def trading_212_asset():
    logging.info("Starting the flow to fetch account cash")
    logging.info("Starting data ingestion process")
    task_run_asset_pipeline()
    logging.info("End data ingestion process")

    
if __name__ == "__main__": 
    trading_212_asset.serve(
        name="trading_212_asset", interval=timedelta(seconds=3600))  # Runs every 5mins