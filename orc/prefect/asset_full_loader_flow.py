import logging
from prefect import flow, task
from datetime import timedelta
from prefect.cache_policies import NO_CACHE
from src.services.ingestion.pipeline_factory import PipelineFactory

from src.shared.utils.custom_logger import customer_logger

logging = customer_logger("asset_flow_run")

@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_run_asset_full_loader_pipeline():
    pipeline = PipelineFactory.get("trading212FullLoaderAssetPipeline")
    pipeline.run()

@flow
def trading_212_asset_full_loader():
    logging.info("Starting the flow to fetch account cash")
    logging.info("Starting data ingestion process")
    task_run_asset_full_loader_pipeline()
    logging.info("End data ingestion process")

    
if __name__ == "__main__": 
    trading_212_asset_full_loader.serve(
        name="asset_full_load_ingestion", interval=timedelta(seconds=600))  # Runs every 5mins