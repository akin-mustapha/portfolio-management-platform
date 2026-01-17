
import json
import logging
from time import sleep
from datetime import datetime, UTC
from src.shared.database.client import SQLModelClient
from src.services.ingestion_service.infrastructure.repositories.entity_repository import EntityRepository
from src.services.ingestion_service.infrastructure.repositories.raw_data_repository import RawDataRepository
from src.services.ingestion_service.application.strategy.strategies import Trading212APIStrategy, AssetSnapshotTLStrategy
from src.shared.utils.custom_logger import customer_logger

logging = customer_logger("ingestion_service")


# Where to Dump data
# How to dump data
# Where to fetch data from
# How to fetch data
class Trading212IngestionService:
    def __init__(self, api_client, fetch=None, dump_strategy=None):
        logging.info("=" * 80)
        logging.info("Initializing Ingestion Service")
        logging.info("=" * 80)
        self.api_client = api_client
        self.dump_strategy = dump_strategy

    def ingest_raw_data(self, endpoint, extraction_strategy, repository):
        results = extraction_strategy.apply_to(endpoint, self.api_client)
        res = repository.insert(
            record={
                "source": endpoint,
                "payload": json.dumps(results),
                "is_processed": False,
                "created_datetime": datetime.now(UTC)
                }
        )
        return res
    
    def asset(self,
            raw_data_repository,
            processed_data_repository,
            extraction_strategy,
            transformation_strategy,
            ):
        endpoint = "equity/positions"
        res = self.ingest_raw_data(endpoint, extraction_strategy, raw_data_repository)
        transformation_strategy.apply_to(res, processed_data_repository)
        raw_data_repository.process_raw_data(res.get('id'))

    # This guy makes Asset Snapshot cake
    # It puts the raw ingredients on the rawDataRepo shelve 
    # It puts the freshly baked cake in the AssetSnapshotRepo
    def asset_snapshot(self,
                raw_data_repository,
                asset_repository,
                asset_snapshot_repository,
                extraction_strategy,
                transformation_strategy,
                ):
        endpoint = "equity/positions"
        res = self.ingest_raw_data(endpoint, extraction_strategy, raw_data_repository)
        transformation_strategy.apply_to(res, asset_repository, asset_snapshot_repository)
        raw_data_repository.process_raw_data(res.get('id'))

    def portfolio_snapshot(self,
                           raw_data_repository,
                           processed_data_repository,
                           extraction_strategy,
                           transformation_strategy,
                           ):
        endpoint = "equity/account/summary"
        res = self.ingest_raw_data(endpoint, extraction_strategy, raw_data_repository)
        transformation_strategy.apply_to(res, processed_data_repository)
        raw_data_repository.process_raw_data(res.get('id'))