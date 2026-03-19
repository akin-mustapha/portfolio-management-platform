import os
import logging
from dotenv import load_dotenv
from typing import List, Any, Dict
from dataclasses import dataclass, asdict

from ...application.protocols import Source
from ...application.policies import Pipeline
from ...application.protocols import Destination
from ...application.protocols import Transformation

# TODO: should depend on interface
from shared.database.client import SQLModelClient
from ...infrastructure.repositories.repository_factory import RepositoryFactory

logging.basicConfig(
    level=logging.INFO,
    filename='logs/info.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s'
)

load_dotenv()

URL = os.getenv("API_URL")
API_TOKEN = os.getenv("API_TOKEN")
SECRET_TOKEN = os.getenv("SECRET_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")


@dataclass
class AccountComputed:
  account_id: str
  total_return_abs: float
  total_return_pct: float
  cash_deployment_ratio: float
  daily_change_abs: float
  daily_change_pct: float


class Trading212AccountComputedSourceSilver(Source):
  def __init__(self):
    self._client = SQLModelClient(DATABASE_URL)

  def extract(self):
    table_name = 'staging.account'
    sql = f"""
            SELECT
                id AS account_id,
                investments_unrealized_pnl,
                investments_realized_pnl,
                investments_total_cost,
                total_value,
                cash_available_to_trade,
                LAG(total_value) OVER (ORDER BY data_timestamp) AS prev_total_value
            FROM {table_name}
    """
    with self._client as db:
      result = db.execute(sql)
    return result.fetchall()


class Trading212AccountComputedTransformation(Transformation):
  def transform(self, data: list[Dict]) -> list[AccountComputed]:
    transformed_data = []
    for record in data:
      record = dict(record._mapping)
      rget = record.get
      investments_unrealized_pnl=0 if (value := rget("investments_unrealized_pnl")) is None else value
      investments_realized_pnl=0 if (value := rget("investments_realized_pnl")) is None else value
      investments_total_cost=0 if (value := rget("investments_total_cost")) is None else value
      total_value=0 if (value := rget("total_value")) is None else value
      cash_available_to_trade=0 if (value := rget("cash_available_to_trade")) is None else value
      prev_total_value=0 if (value := rget("prev_total_value")) is None else value
      total_return_abs = investments_unrealized_pnl + investments_realized_pnl
      total_return_pct = 0 if investments_total_cost == 0 else (investments_unrealized_pnl + investments_realized_pnl) / investments_total_cost * 100
      cash_deployment_ratio = 0 if total_value == 0 else (total_value - cash_available_to_trade) / total_value * 100
      daily_change_abs = 0 if prev_total_value == 0 else total_value - prev_total_value
      daily_change_pct = 0 if prev_total_value == 0 else daily_change_abs / prev_total_value * 100
      transformed_data.append(
        AccountComputed(
          account_id=rget("account_id"),
          total_return_abs=total_return_abs,
          total_return_pct=total_return_pct,
          cash_deployment_ratio=cash_deployment_ratio,
          daily_change_abs=daily_change_abs,
          daily_change_pct=daily_change_pct,
        )
      )
    return transformed_data


class Trading212AccountComputedDestination(Destination):
  def __init__(self):
      self._repository = RepositoryFactory.get("account_computed", schema_name="staging")

  def load(self, data: List[Dict]) -> None:
      self._repository.upsert(records=data, unique_key=['account_id'])


class PipelineAccountComputedSilver(Pipeline):
  def __init__(self):
    self._source = Trading212AccountComputedSourceSilver()
    self._transformation = Trading212AccountComputedTransformation()
    self._destination = Trading212AccountComputedDestination()

  def run(self):
    # Fetch raw data from source
    data = self._source.extract()

    try:
      # Apply Transformation Logic
      transformed_data: List[Any] = self._transformation.transform(data)

      # Mapping
      data = [
        asdict(
          row
        )
        for row in transformed_data
      ]

      # Save to Destination Table
      self._destination.load(data)
      return None

    except Exception as e:
      raise e


if __name__ == "__main__":
  PipelineAccountComputedSilver().run()
