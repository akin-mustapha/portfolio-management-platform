"""
Backfill script: raw.account + raw.asset → raw.t212_snapshot

Pairs legacy bronze records (separate account and asset tables) into unified
snapshot rows matching the raw.t212_snapshot schema.

Matching strategy:
  - Account data leads: one snapshot per 15-minute slot (earliest per slot).
  - Assets matched within ASSET_WINDOW_MINUTES (default: 10) after the account timestamp.
  - Idempotent: skips 15-min slots already present in raw.t212_snapshot.

Usage:
  python scripts/backfill_raw_snapshot.py
  python scripts/backfill_raw_snapshot.py --asset-window-minutes 10
  python scripts/backfill_raw_snapshot.py --dry-run
"""

import argparse
import json
import logging
import os
import sys
import uuid
from datetime import timedelta

from dotenv import load_dotenv

# Allow imports from src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from v2.shared.database.client import SQLModelClient  # noqa: E402

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

# Size of the account dedup bucket — one snapshot per this many minutes
SLOT_MINUTES = 15


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

# Existing 15-min slots already in raw.t212_snapshot (for idempotency)
EXISTING_SLOTS_SQL = f"""
SELECT DISTINCT
    ingested_date,
    to_timestamp(floor(extract(epoch from ingested_timestamp) / ({SLOT_MINUTES} * 60)) * ({SLOT_MINUTES} * 60))
        AT TIME ZONE 'UTC' AS ingested_slot
FROM raw.t212_snapshot
"""

# One account record per 15-min slot — earliest ingested_timestamp wins
ACCOUNT_DEDUPED_SQL = f"""
WITH ranked AS (
    SELECT
        payload,
        ingested_date,
        ingested_timestamp,
        to_timestamp(floor(extract(epoch from ingested_timestamp) / ({SLOT_MINUTES} * 60)) * ({SLOT_MINUTES} * 60))
            AT TIME ZONE 'UTC' AS ingested_slot,
        ROW_NUMBER() OVER (
            PARTITION BY
                ingested_date,
                floor(extract(epoch from ingested_timestamp) / ({SLOT_MINUTES} * 60))
            ORDER BY ingested_timestamp ASC
        ) AS rn
    FROM raw.account
)
SELECT
    payload           AS account_data,
    ingested_date,
    ingested_slot,
    ingested_timestamp
FROM ranked
WHERE rn = 1
ORDER BY ingested_date ASC, ingested_slot ASC
"""

ASSETS_FOR_WINDOW_SQL = """
SELECT payload
FROM raw.asset
WHERE ingested_timestamp >= :start_ts
  AND ingested_timestamp <= :end_ts
ORDER BY ingested_timestamp ASC
"""

INSERT_SNAPSHOT_SQL = """
INSERT INTO raw.t212_snapshot (id, ingested_date, ingested_timestamp, account_data, position_data)
VALUES (:id, :ingested_date, :ingested_timestamp, :account_data, :position_data)
"""

CREATE_PARTITION_SQL = """
CREATE TABLE IF NOT EXISTS {partition_name}
PARTITION OF raw.t212_snapshot
FOR VALUES FROM ('{day}') TO ('{next_day}')
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_existing_slots(client: SQLModelClient) -> set:
    """Return set of (ingested_date, ingested_slot) already in raw.t212_snapshot."""
    result = client.execute(EXISTING_SLOTS_SQL)
    return {(row[0], row[1]) for row in result}


def _load_account_records(client: SQLModelClient) -> list:
    """Return deduplicated account records — one per 15-min slot."""
    result = client.execute(ACCOUNT_DEDUPED_SQL)
    rows = []
    for row in result:
        rows.append(
            {
                "account_data": row[0],
                "ingested_date": row[1],
                "ingested_slot": row[2],
                "ingested_timestamp": row[3],
            }
        )
    return rows


def _ensure_partition(client: SQLModelClient, ingested_date, dry_run: bool) -> None:
    """Create the date partition for raw.t212_snapshot if it doesn't exist."""
    from datetime import date, timedelta

    if isinstance(ingested_date, str):
        ingested_date = date.fromisoformat(ingested_date)
    next_day = ingested_date + timedelta(days=1)
    partition_name = f"raw.t212_snapshot_{ingested_date.strftime('%Y_%m_%d')}"
    sql = CREATE_PARTITION_SQL.format(
        partition_name=partition_name,
        day=ingested_date.isoformat(),
        next_day=next_day.isoformat(),
    )
    if not dry_run:
        client.execute(sql)
    logger.debug("Ensured partition: %s", partition_name)


def _load_assets_for_window(client: SQLModelClient, start_ts, end_ts) -> list:
    """Return asset payload dicts within the time window."""
    result = client.execute(
        ASSETS_FOR_WINDOW_SQL,
        {"start_ts": start_ts, "end_ts": end_ts},
    )
    return [row[0] for row in result]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def run(asset_window_minutes: int = 10, dry_run: bool = False) -> None:
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable is not set.")

    logger.info(
        "Starting raw snapshot backfill (slot=%d min, asset_window=%d min, dry_run=%s)",
        SLOT_MINUTES,
        asset_window_minutes,
        dry_run,
    )

    client = SQLModelClient(DATABASE_URL)
    client.connect()

    try:
        existing_slots = _load_existing_slots(client)
        logger.info(
            "Found %d existing 15-min slots in raw.t212_snapshot — will skip these.",
            len(existing_slots),
        )

        account_records = _load_account_records(client)
        logger.info(
            "Found %d deduplicated account records to process.", len(account_records)
        )

        skipped = 0
        inserted = 0
        empty_position_warnings = 0
        partitioned_dates: set = set()

        for rec in account_records:
            slot = (rec["ingested_date"], rec["ingested_slot"])

            if slot in existing_slots:
                skipped += 1
                continue

            if rec["ingested_date"] not in partitioned_dates:
                _ensure_partition(client, rec["ingested_date"], dry_run)
                partitioned_dates.add(rec["ingested_date"])

            start_ts = rec["ingested_timestamp"]
            end_ts = start_ts + timedelta(minutes=asset_window_minutes)

            assets = _load_assets_for_window(client, start_ts, end_ts)

            if not assets:
                empty_position_warnings += 1
                logger.warning(
                    "No assets for slot %s / %s (window: %s → %s)",
                    rec["ingested_date"],
                    rec["ingested_slot"],
                    start_ts,
                    end_ts,
                )

            snapshot = {
                "id": str(uuid.uuid4()),
                "ingested_date": rec["ingested_date"],
                "ingested_timestamp": start_ts,
                "account_data": json.dumps(rec["account_data"])
                if isinstance(rec["account_data"], dict)
                else rec["account_data"],
                "position_data": json.dumps(assets),
            }

            logger.info(
                "  [%s] %s — %d assets%s",
                rec["ingested_date"],
                rec["ingested_slot"],
                len(assets),
                " (NO ASSETS)" if not assets else "",
            )

            if not dry_run:
                client.execute(INSERT_SNAPSHOT_SQL, snapshot)

            inserted += 1

        logger.info(
            "Backfill complete. Inserted: %d | Skipped (already exist): %d | Empty position warnings: %d",
            inserted,
            skipped,
            empty_position_warnings,
        )
        if dry_run:
            logger.info("DRY RUN — no rows were written.")

    finally:
        client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Backfill raw.t212_snapshot from raw.account + raw.asset"
    )
    parser.add_argument(
        "--asset-window-minutes",
        type=int,
        default=10,
        help="Minutes after account ingestion to collect matching assets (default: 10)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be inserted without writing to the database",
    )
    args = parser.parse_args()
    run(asset_window_minutes=args.asset_window_minutes, dry_run=args.dry_run)
