import os
import logging
from dotenv import load_dotenv
from datetime import datetime, UTC
from typing import List, Dict
import pandas as pd

from ...application.policies import BaseSilverPipeline
from ...application.protocols import Source
from ...application.protocols import Destination
from ...application.protocols import Transformation
from ...application.validators.schema_validator import SchemaValidator

# TODO: should depend on interface
from shared.database.client import SQLModelClient
from ...infrastructure.repositories.repository_factory import RepositoryFactory
from ...infrastructure.repositories.dead_letter_destination import DeadLetterDestination
from ...domain.schemas.silver.account import AccountRecord

logging.basicConfig(
    level=logging.INFO,
    filename="logs/info.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


class Trading212AccountSourceSilver(Source):
    def __init__(self):
        self._client = SQLModelClient(DATABASE_URL)

    def extract(self):
        sql = """
      SELECT
        external_id,
        cash_in_pies,
        cash_available_to_trade,
        cash_reserved_for_orders,
        currency,
        total_value,
        investments_total_cost,
        investments_realized_pnl,
        investments_unrealized_pnl,
        ingested_date,
        ingested_timestamp,
        business_key
      FROM raw.v_bronze_account t1
      WHERE NOT EXISTS (
            SELECT 1
            FROM staging.account x1
            WHERE t1.business_key = x1.business_key
          )
          AND external_id IS NOT NULL
    """

        with self._client as db:
            result = db.execute(sql)

        # TODO: Convert result to data
        return result.fetchall()


class Trading212AccountTransformationSilver(Transformation):
    """
    Trading212AccountTransformationSilver
    """

    def transform(self, data: list[Dict]) -> list[Dict]:
        """
        transform
        """
        bronze_account_df = pd.DataFrame(data)
        # REMOVE NULL
        df = bronze_account_df[bronze_account_df["external_id"].notna()]

        account_df = pd.DataFrame()
        account_df["external_id"] = df["external_id"]
        account_df["cash_in_pies"] = df["cash_in_pies"]
        account_df["cash_available_to_trade"] = df["cash_available_to_trade"]
        account_df["cash_reserved_for_orders"] = df["cash_reserved_for_orders"]
        account_df["broker"] = "Trading 212"
        account_df["currency"] = df["currency"]
        account_df["total_value"] = df["total_value"]
        account_df["investments_total_cost"] = df["investments_total_cost"]
        account_df["investments_realized_pnl"] = df["investments_realized_pnl"]
        account_df["investments_unrealized_pnl"] = df["investments_unrealized_pnl"]
        account_df["business_key"] = df["business_key"]
        account_df["updated_timestamp"] = datetime.now(UTC)

        # Using ingested date as marker to sequential ordering of data
        account_df["data_timestamp"] = df["ingested_timestamp"]
        asset_dict = account_df.to_dict("records")
        return asset_dict


class Trading212AccountDestination(Destination):
    def __init__(self):
        # TODO: INJECT DEPENDENCY MAKES TESTING EASIER | ALLOWS TO CHANGE BEHAVIOUR
        self._repository = RepositoryFactory.get("account", schema_name="staging")

    def load(self, data: List[Dict]) -> None:
        self._repository.upsert(records=data, unique_key=["business_key"])


class PipelineAccountSilver(BaseSilverPipeline):
    _pipeline_name = "account_silver"

    def __init__(self):
        self._source = Trading212AccountSourceSilver()
        self._transformation = Trading212AccountTransformationSilver()
        self._validator = SchemaValidator(AccountRecord)
        self._destination = Trading212AccountDestination()
        self._dead_letter = DeadLetterDestination()


if __name__ == "__main__":
    PipelineAccountSilver().run()
