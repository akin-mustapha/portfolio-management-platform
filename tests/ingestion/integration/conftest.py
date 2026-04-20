"""
Integration-test fixtures for the T212 history raw ingestion.

Connects to the Postgres instance defined in docker-compose.yml via the
DATABASE_URL env var. If the DB is unreachable, tests that depend on these
fixtures are skipped so CI runs without a DB still pass.

The postgres_raw_history_schema fixture applies the 005 migration DDL
directly (not via Alembic) and drops the tables on teardown, so each test
run starts and ends clean without interfering with a developer's dev DB.
"""

import os

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

_CREATE_SQL = """
CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.t212_history_dividend (
    id                  TEXT NOT NULL,
    ingested_date       DATE NOT NULL,
    ingested_timestamp  TIMESTAMPTZ DEFAULT now(),
    payload             JSONB NOT NULL,
    processed_at        TIMESTAMPTZ,
    PRIMARY KEY (id, ingested_date)
) PARTITION BY RANGE (ingested_date);

CREATE TABLE IF NOT EXISTS raw.t212_history_order (
    id                  TEXT NOT NULL,
    ingested_date       DATE NOT NULL,
    ingested_timestamp  TIMESTAMPTZ DEFAULT now(),
    payload             JSONB NOT NULL,
    processed_at        TIMESTAMPTZ,
    PRIMARY KEY (id, ingested_date)
) PARTITION BY RANGE (ingested_date);

CREATE TABLE IF NOT EXISTS raw.t212_history_transaction (
    id                  TEXT NOT NULL,
    ingested_date       DATE NOT NULL,
    ingested_timestamp  TIMESTAMPTZ DEFAULT now(),
    payload             JSONB NOT NULL,
    processed_at        TIMESTAMPTZ,
    PRIMARY KEY (id, ingested_date)
) PARTITION BY RANGE (ingested_date);

CREATE TABLE IF NOT EXISTS raw.t212_history_cursor (
    endpoint       TEXT PRIMARY KEY,
    last_cursor    TEXT,
    last_event_ts  TIMESTAMPTZ,
    updated_at     TIMESTAMPTZ DEFAULT now()
);
"""

_DROP_SQL = """
DROP TABLE IF EXISTS raw.t212_history_cursor CASCADE;
DROP TABLE IF EXISTS raw.t212_history_transaction CASCADE;
DROP TABLE IF EXISTS raw.t212_history_order CASCADE;
DROP TABLE IF EXISTS raw.t212_history_dividend CASCADE;
"""


@pytest.fixture(scope="module")
def postgres_raw_history_schema():
    if not DATABASE_URL or not DATABASE_URL.startswith("postgresql"):
        pytest.skip("DATABASE_URL not configured for Postgres")

    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        pytest.skip(f"Postgres not reachable: {e}")

    with engine.begin() as conn:
        for stmt in filter(None, (s.strip() for s in _CREATE_SQL.split(";"))):
            conn.execute(text(stmt))

    yield engine

    with engine.begin() as conn:
        for stmt in filter(None, (s.strip() for s in _DROP_SQL.split(";"))):
            conn.execute(text(stmt))
    engine.dispose()
