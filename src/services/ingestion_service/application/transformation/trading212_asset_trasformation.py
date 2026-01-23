import json
from datetime import datetime, UTC
from typing import Iterable, Any, List, Dict
from src.services.ingestion_service.application.interfaces.protocols.transformation import Transformation

class Trading212AssetTransformation(Transformation):
  def apply_to(self, record: str) -> List[Dict]:
    # assets = json.loads(record.get('payload', {}))
    transformed_data = []
    for asset in record:
      instrument = asset.get("instrument", {})
      data = dict(
          # TODO: Map to config
          external_id=instrument.get("ticker"),
          name=instrument.get("ticker"),
          description=instrument.get("name"),
          source_name="trading212",
          is_active=True,
          created_datetime=datetime.now(UTC),
      )
      transformed_data.append(data)
    return transformed_data