import logging
from prefect import flow, task
from datetime import timedelta
from prefect.cache_policies import NO_CACHE
from src.shared.utils.custom_logger import customer_logger
from src.kafka.asset_event_producer import AssetEventProducer

logging = customer_logger("asset_flow_run")

@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_run_trading_212_asset_event_producer():
    producer = AssetEventProducer()
    producer.run()
@flow
def trading_212_asset_event_producer():

    logging.info("Starting the flow to fetch account cash")
    logging.info("Starting data ingestion process")
    task_run_trading_212_asset_event_producer()
    logging.info("End data ingestion process")

    
if __name__ == "__main__": 
    trading_212_asset_event_producer.serve(
        name="trading_212_asset_event_producer", interval=timedelta(seconds=600))  # Runs every 5mins