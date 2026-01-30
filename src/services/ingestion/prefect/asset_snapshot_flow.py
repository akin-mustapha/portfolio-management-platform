import logging
from prefect import flow, task
from datetime import timedelta
from prefect.cache_policies import NO_CACHE
from src.services.ingestion.app.pipelines. pipeline_factory import PipelineFactory

from src.shared.utils.custom_logger import customer_logger

logging = customer_logger("asset_snapshot_flow_run")

@task(retry_delay_seconds=30, retries=2, cache_policy=NO_CACHE)
def ingest_asset_snapshot():
    pipeline = PipelineFactory.get("trading212AssetSnapshotPipeline")
    pipeline.run()

@flow
def trading_212_asset_snapshot():
    logging.info("Starting the flow to fetch account cash")
    logging.info("Starting data ingestion process")
    ingest_asset_snapshot()
    logging.info("End data ingestion process")

    
if __name__ == "__main__": 
    trading_212_asset_snapshot.serve(
        name="trading_212_asset_snapshot", interval=timedelta(seconds=3600))  # Runs every 5mins