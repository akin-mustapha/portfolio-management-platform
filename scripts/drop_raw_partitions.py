"""
Drop old raw partition tables for raw.asset and raw.account.

Discovers and drops all child partition tables while leaving the parent
tables (raw.asset, raw.account) intact.

Usage:
  python scripts/drop_raw_partitions.py               # dry-run (default)
  python scripts/drop_raw_partitions.py --execute     # drop with confirmation
  python scripts/drop_raw_partitions.py --execute --yes  # drop without prompt
"""

import argparse
import logging
import os
import sys

from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from shared.database.client import SQLModelClient  # noqa: E402

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

DISCOVER_PARTITIONS_SQL = """
SELECT
    n.nspname || '.' || c.relname AS partition_name
FROM pg_inherits i
JOIN pg_class c   ON c.oid  = i.inhrelid
JOIN pg_class p   ON p.oid  = i.inhparent
JOIN pg_namespace n  ON n.oid = c.relnamespace
JOIN pg_namespace pn ON pn.oid = p.relnamespace
WHERE pn.nspname = 'raw'
  AND p.relname = ANY(:tables)
ORDER BY partition_name
"""


def _discover_partitions(client: SQLModelClient, tables: list[str]) -> list[str]:
    result = client.execute(DISCOVER_PARTITIONS_SQL, {"tables": tables})
    return [row[0] for row in result]


def run(execute: bool = False, yes: bool = False, tables: list[str] | None = None) -> None:
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable is not set.")

    if tables is None:
        tables = ["asset", "account"]

    client = SQLModelClient(DATABASE_URL)
    client.connect()

    try:
        partitions = _discover_partitions(client, tables)

        if not partitions:
            logger.info("No partitions found for: %s", tables)
            return

        logger.info("Found %d partition(s) to drop:", len(partitions))
        for p in partitions:
            logger.info("  %s", p)

        if not execute:
            logger.info("\nDRY RUN — no changes made. Pass --execute to drop.")
            return

        if not yes:
            answer = input(f"\nDrop {len(partitions)} partition(s)? [y/N] ").strip().lower()
            if answer != "y":
                logger.info("Aborted.")
                return

        for partition in partitions:
            sql = f"DROP TABLE IF EXISTS {partition}"
            client.execute(sql)
            logger.info("Dropped: %s", partition)

        # Verify
        remaining = _discover_partitions(client, tables)
        if remaining:
            logger.warning("Some partitions still exist: %s", remaining)
        else:
            logger.info("All partitions dropped. Parent tables raw.%s remain intact.", " / raw.".join(tables))

    finally:
        client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Drop old raw partition tables")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually drop the partitions (default is dry-run)",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompt",
    )
    parser.add_argument(
        "--tables",
        nargs="+",
        default=["asset", "account"],
        help="Parent table names to target (default: asset account)",
    )
    args = parser.parse_args()
    run(execute=args.execute, yes=args.yes, tables=args.tables)
