import logging
from prefect import flow, task
from datetime import timedelta
from prefect.cache_policies import NO_CACHE
from src.services.analytics.app.silver_asset import SilverAsset
from src.services.analytics.query import AssetSilverQueryRepo
from src.services.analytics.funcs import FuncAssetDerivedMetric
from src.services.analytics.sink import SinkSilverAsset

from src.shared.utils.custom_logger import customer_logger

logging = customer_logger("asset_flow_run")

@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_run_silver_layer_asset_ingestion():
    pipeline = SilverAsset(AssetSilverQueryRepo
                      , FuncAssetDerivedMetric
                      , SinkSilverAsset)
    pipeline.run()

@flow
def trading_212_asset_silver_incremental_loader():
    logging.info("Starting the flow to fetch account cash")
    logging.info("Starting data ingestion process")
    task_run_silver_layer_asset_ingestion()
    logging.info("End data ingestion process")

    
if __name__ == "__main__": 
    trading_212_asset_silver_incremental_loader.serve(
        name="asset_silver_pipeline", interval=timedelta(seconds=600))  # Runs every 5mins