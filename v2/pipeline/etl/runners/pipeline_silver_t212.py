"""
Unified Silver Pipeline for Trading212

Reads a full snapshot from raw.t212_snapshot (account + positions together)
and writes to staging.asset and staging.account in a single run.
"""

import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Any

from pipeline.domain.schemas.silver.asset import AssetRecord
from pipeline.domain.schemas.silver.account import AccountRecord

from pipeline.etl.policies import Pipeline
from pipeline.etl.protocols import Source, Destination, Transformation, RejectedRecord
from pipeline.etl.validators.schema_validator import SchemaValidator

# TODO: should depend on interface
from shared.database.client import SQLModelClient
from shared.database.query_loader import load_query
from pipeline.infrastructure.repositories.repository_factory import RepositoryFactory
from pipeline.infrastructure.repositories.dead_letter_destination import (
    DeadLetterDestination,
)

_QUERIES_DIR = Path(__file__).parent.parent.parent / "infrastructure" / "queries"


def _reject(
    errors: List[RejectedRecord],
    snapshot_id: str,
    raw: Any,
    error_type: str,
    error_message: str,
) -> None:
    errors.append(
        RejectedRecord(
            pipeline_name=None,
            layer="silver",
            business_key=snapshot_id,
            raw_payload={"snapshot_id": snapshot_id, "raw": str(raw)[:500]},
            error_type=error_type,
            error_message=error_message,
        )
    )


logging.basicConfig(
    level=logging.INFO,
    filename="logs/info.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


# ─────────────────────────────────────────────
# Source
# ─────────────────────────────────────────────


class Trading212SilverSource(Source):
    def __init__(self):
        self._client = SQLModelClient(DATABASE_URL)
        self._sql = load_query(_QUERIES_DIR / "silver" / "t212_silver_source.sql")

    def extract(self) -> List[Any]:
        with self._client as db:
            result = db.execute(self._sql)
        return result.fetchall()


# ─────────────────────────────────────────────
# Transformations
# ─────────────────────────────────────────────


class Trading212AssetTransformationSilver(Transformation):
    @property
    def parse_errors(self) -> List[RejectedRecord]:
        return self._parse_errors

    def transform(self, snapshots: List[Any]) -> List[Dict]:
        self._parse_errors: List[RejectedRecord] = []
        records = []
        for row in snapshots:
            snapshot_id = row.snapshot_id
            ingested_timestamp = row.ingested_timestamp
            positions = row.position_data
            if isinstance(positions, str):
                try:
                    positions = json.loads(positions)
                except json.JSONDecodeError as e:
                    _reject(
                        self._parse_errors,
                        snapshot_id,
                        positions,
                        "JSONDecodeError",
                        str(e),
                    )
                    continue

            for pos in positions:
                if not isinstance(pos, dict):
                    pos_str = str(pos)
                    _reject(
                        self._parse_errors,
                        snapshot_id,
                        pos_str,
                        "InvalidPositionEntry",
                        f"Expected dict, got {type(pos).__name__}: {pos_str[:100]}",
                    )
                    continue

                if not pos.get("instrument", {}).get("ticker"):
                    continue

                full_ticker = pos["instrument"]["ticker"]
                ticker = full_ticker.split("_")[0]
                wallet = pos.get("walletImpact", {})

                records.append(
                    {
                        "external_id": full_ticker,
                        "ticker": ticker,
                        "name": pos["instrument"]["name"],
                        "description": pos["instrument"]["name"],
                        "broker": "Trading 212",
                        "currency": pos["instrument"]["currency"],
                        "local_currency": wallet.get("currency", ""),
                        "share": pos.get("quantity", 0.0),
                        "price": pos.get("currentPrice", 0.0),
                        "avg_price": pos.get("averagePricePaid", 0.0),
                        "value": wallet.get("currentValue", 0.0),
                        "cost": wallet.get("totalCost", 0.0),
                        "profit": wallet.get("unrealizedProfitLoss", 0.0),
                        "fx_impact": wallet.get("fxImpact") or 0.0,
                        "quantity_in_pies": pos.get("quantityInPies") or 0.0,
                        "snapshot_id": snapshot_id,
                        "business_key": f"{snapshot_id}_{full_ticker}_{ingested_timestamp}",
                        "data_timestamp": ingested_timestamp,
                    }
                )
        return records


class Trading212AccountTransformationSilver(Transformation):
    @property
    def parse_errors(self) -> List[RejectedRecord]:
        return self._parse_errors

    def transform(self, snapshots: List[Any]) -> List[Dict]:
        self._parse_errors: List[RejectedRecord] = []
        records = []
        for row in snapshots:
            account = row.account_data
            if isinstance(account, str):
                try:
                    account = json.loads(account)
                except json.JSONDecodeError as e:
                    _reject(
                        self._parse_errors,
                        row.snapshot_id,
                        account,
                        "JSONDecodeError",
                        str(e),
                    )
                    continue
            if not account:
                continue

            external_id = str(account.get("id", ""))
            currency = account.get("currency", "")
            cash = account.get("cash", {})
            investments = account.get("investments", {})

            records.append(
                {
                    "external_id": external_id,
                    "cash_in_pies": cash.get("inPies", 0.0),
                    "cash_available_to_trade": cash.get("availableToTrade", 0.0),
                    "cash_reserved_for_orders": cash.get("reservedForOrders", 0.0),
                    "broker": "Trading 212",  # Todo: Hardcoded broker Name
                    "currency": currency,
                    "total_value": account.get("totalValue", 0.0),
                    "investments_total_cost": investments.get("totalCost", 0.0),
                    "investments_realized_pnl": investments.get(
                        "realizedProfitLoss", 0.0
                    ),
                    "investments_unrealized_pnl": investments.get(
                        "unrealizedProfitLoss", 0.0
                    ),
                    "snapshot_id": row.snapshot_id,
                    "business_key": f"{external_id}_{currency}_{row.ingested_timestamp}",
                    "data_timestamp": row.ingested_timestamp,
                }
            )
        return records


# ─────────────────────────────────────────────
# Destinations
# ─────────────────────────────────────────────


class AssetSilverDestination(Destination):
    def __init__(self):
        self._repository = RepositoryFactory.get("asset", schema_name="staging")

    def load(self, data: List[Dict]) -> None:
        self._repository.upsert(records=data, unique_key=["business_key"])


class AccountSilverDestination(Destination):
    def __init__(self):
        self._repository = RepositoryFactory.get("account", schema_name="staging")

    def load(self, data: List[Dict]) -> None:
        self._repository.upsert(records=data, unique_key=["business_key"])


# ─────────────────────────────────────────────
# Pipeline
# ─────────────────────────────────────────────


class PipelineT212Silver(Pipeline):
    _pipeline_name = "t212_silver"

    def __init__(self):
        self._source = Trading212SilverSource()
        self._asset_transformation = Trading212AssetTransformationSilver()
        self._account_transformation = Trading212AccountTransformationSilver()
        self._asset_validator = SchemaValidator(AssetRecord)
        self._account_validator = SchemaValidator(AccountRecord)
        self._asset_destination = AssetSilverDestination()
        self._account_destination = AccountSilverDestination()
        self._dead_letter = DeadLetterDestination()

    def run(self):
        snapshots = self._source.extract()

        if not snapshots:
            logging.warning(f"[{self._pipeline_name}] NO RECORD")
            return

        asset_data = self._asset_transformation.transform(snapshots)
        account_data = self._account_transformation.transform(snapshots)

        parse_errors = (
            self._asset_transformation.parse_errors
            + self._account_transformation.parse_errors
        )
        if parse_errors:
            for r in parse_errors:
                r.pipeline_name = self._pipeline_name
            self._dead_letter.load(parse_errors)
            logging.warning(
                f"[{self._pipeline_name}] {len(parse_errors)} snapshots rejected — invalid JSON in JSONB column"
            )

        asset_result = self._asset_validator.validate(asset_data)
        account_result = self._account_validator.validate(account_data)

        for result, name in [
            (asset_result, f"{self._pipeline_name}_asset"),
            (account_result, f"{self._pipeline_name}_account"),
        ]:
            if result.invalid:
                for r in result.invalid:
                    r.pipeline_name = name
                self._dead_letter.load(result.invalid)
                logging.warning(f"[{name}] {len(result.invalid)} records rejected")

        self._asset_destination.load([r.model_dump() for r in asset_result.valid])
        self._account_destination.load([r.model_dump() for r in account_result.valid])


if __name__ == "__main__":
    PipelineT212Silver().run()
