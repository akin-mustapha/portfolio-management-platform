from prefect import flow, task
from prefect.cache_policies import NO_CACHE
from prefect.logging import get_run_logger

from pipeline.infrastructure.factories.event_producer_factory import (
    EventProducerFactory,
)


@task(retry_delay_seconds=60, retries=2, cache_policy=NO_CACHE)
def task_run_trading_212_asset_event_producer():
    producer = EventProducerFactory.get("trading212AssetEventProducer")
    producer.run()


@flow
def trading_212_asset_event_producer():
    logging = get_run_logger()
    logging.info("Starting Flow")
    task_run_trading_212_asset_event_producer()
    logging.info("End")
