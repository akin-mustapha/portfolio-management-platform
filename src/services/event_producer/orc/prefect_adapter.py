import logging
from prefect import flow, task
from datetime import timedelta
from prefect.cache_policies import NO_CACHE
from prefect.logging import get_run_logger

from ..trading212_event_producer import Trading212EventProducer
from ..infra.origins import Trading212AssetAPIOrigin
from ..infra.destination import Trading212KafkaDestination


@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_run_trading_212_asset_event_producer():
    producer = Trading212EventProducer(
        origin=Trading212AssetAPIOrigin("Trading212_Asset_API"),
        destination=Trading212KafkaDestination("Kafka")
        )
    producer.run()
@flow
def trading_212_asset_event_producer():
    logging = get_run_logger()
    logging.info("Starting Flow")
    task_run_trading_212_asset_event_producer()
    logging.info("End")

    
def deploy():
    trading_212_asset_event_producer.serve(
        name="trading_212_asset_event_producer", interval=timedelta(seconds=600))  # Runs every 5mins