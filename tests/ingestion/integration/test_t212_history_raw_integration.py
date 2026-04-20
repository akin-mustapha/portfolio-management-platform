"""
Integration test: T212 history bronze pipeline against a real Postgres.

Stubs the T212 API client with canned JSON pages (no external HTTP) and
verifies that rows and cursor state land in the expected raw tables,
and that a second run with the same fixtures is idempotent.

Requires Postgres reachable via DATABASE_URL (see docker-compose.yml).
Skipped automatically if the DB isn't reachable.
"""

from datetime import date
from unittest.mock import patch

from sqlalchemy import text


_DIVIDEND_PAGE = {
    "items": [
        {
            "reference": "DIV-001",
            "paidOn": "2026-04-19T12:00:00Z",
            "amount": 1.23,
            "ticker": "AAPL_US_EQ",
            "type": "ORDINARY",
        },
        {
            "reference": "DIV-002",
            "paidOn": "2026-04-18T12:00:00Z",
            "amount": 2.34,
            "ticker": "MSFT_US_EQ",
            "type": "ORDINARY",
        },
    ],
    "nextPagePath": None,
}

_ORDER_PAGE = {
    "items": [
        {
            "order": {
                "id": 987654321,
                "createdAt": "2026-04-19T09:00:00Z",
                "ticker": "AAPL_US_EQ",
                "status": "FILLED",
            },
            "fill": {"id": 111, "price": 150.0, "quantity": 1},
        },
    ],
    "nextPagePath": None,
}

_TRANSACTION_PAGE = {
    "items": [
        {
            "reference": "TXN-001",
            "dateTime": "2026-04-19T10:00:00Z",
            "amount": 100.0,
            "currency": "GBP",
            "type": "DEPOSIT",
        },
    ],
    "nextPagePath": None,
}


def _fake_paginated_factory():
    async def fake_paginated(endpoint, cursor=None, limit=50, stop_predicate=None):
        if endpoint.endswith("history/dividends"):
            yield _DIVIDEND_PAGE
        elif endpoint.endswith("history/orders"):
            yield _ORDER_PAGE
        elif endpoint.endswith("history/transactions"):
            yield _TRANSACTION_PAGE
        else:
            raise AssertionError(f"unexpected endpoint: {endpoint}")
    return fake_paginated


def _run_pipeline():
    from pipelines.application.runners.pipeline_bronze_t212_history import (
        PipelineT212History,
    )
    from pipelines.infrastructure.clients.api_client_trading212 import (
        Trading212APIClient,
    )

    with patch.object(Trading212APIClient, "get_paginated", _fake_paginated_factory()):
        PipelineT212History().run()


def _table_counts(engine):
    with engine.connect() as conn:
        return {
            "dividend": conn.execute(
                text("SELECT count(*) FROM raw.t212_history_dividend")
            ).scalar(),
            "order": conn.execute(
                text("SELECT count(*) FROM raw.t212_history_order")
            ).scalar(),
            "transaction": conn.execute(
                text("SELECT count(*) FROM raw.t212_history_transaction")
            ).scalar(),
            "cursor": conn.execute(
                text("SELECT count(*) FROM raw.t212_history_cursor")
            ).scalar(),
        }


def test_full_pipeline_writes_rows_and_cursor_and_is_idempotent(
    postgres_raw_history_schema,
):
    engine = postgres_raw_history_schema

    # Run 1 — expect all rows and cursor state to land.
    _run_pipeline()

    counts = _table_counts(engine)
    assert counts == {"dividend": 2, "order": 1, "transaction": 1, "cursor": 3}

    with engine.connect() as conn:
        # Partition for today must exist for at least the dividend parent.
        today_partition = f"raw.t212_history_dividend_{date.today().strftime('%Y_%m_%d')}"
        exists = conn.execute(
            text(
                "SELECT to_regclass(:name) IS NOT NULL AS exists"
            ),
            {"name": today_partition},
        ).scalar()
        assert exists is True

        # JSONB round-trip preserves payload.
        payload = conn.execute(
            text(
                "SELECT payload FROM raw.t212_history_dividend WHERE id = 'DIV-001'"
            )
        ).scalar()
        assert payload["ticker"] == "AAPL_US_EQ"
        assert payload["type"] == "ORDINARY"

        # Cursor populated with newest event timestamp per endpoint.
        cursor_rows = {
            row.endpoint: row
            for row in conn.execute(
                text(
                    "SELECT endpoint, last_cursor, last_event_ts "
                    "FROM raw.t212_history_cursor"
                )
            )
        }
        assert set(cursor_rows) == {"dividends", "orders", "transactions"}
        assert cursor_rows["dividends"].last_event_ts is not None

    # Run 2 — same fixtures. ON CONFLICT DO NOTHING keeps counts flat.
    cursor_before = cursor_rows["dividends"].last_event_ts

    _run_pipeline()

    counts_after = _table_counts(engine)
    assert counts_after == counts, "second run must be idempotent"

    with engine.connect() as conn:
        cursor_after = conn.execute(
            text(
                "SELECT last_event_ts FROM raw.t212_history_cursor "
                "WHERE endpoint = 'dividends'"
            )
        ).scalar()
    assert cursor_after == cursor_before, "cursor must not regress on re-run"
