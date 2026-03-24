import json
import dataclasses
from datetime import datetime, date
from decimal import Decimal

from psycopg2.extras import Json

from ...infrastructure.repositories.repository_factory import RepositoryFactory


def _json_default(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    return str(obj)


class DeadLetterDestination:
    """
    Destination implementation that writes rejected records to monitoring.dead_letter.
    Reuses the Destination protocol — load() receives list[RejectedRecord].
    raw_payload is wrapped with psycopg2.extras.Json so psycopg2 can adapt it to JSONB.
    """

    def __init__(self):
        self._repository = RepositoryFactory.get(
            "dead_letter", schema_name="monitoring"
        )

    def load(self, data: list) -> None:
        records = []
        for r in data:
            record = dataclasses.asdict(r)
            record["raw_payload"] = Json(
                record["raw_payload"],
                dumps=lambda v: json.dumps(v, default=_json_default),
            )
            records.append(record)
        self._repository.insert(records=records)
