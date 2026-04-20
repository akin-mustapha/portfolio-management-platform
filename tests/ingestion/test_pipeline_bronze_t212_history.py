"""
Unit tests for the T212 historical-events bronze pipeline.

Covers:
  - Source paginates until nextPagePath is null
  - Source stops when stored high-water mark is reached
  - One endpoint failing does not prevent the others from being extracted
  - Loader inserts per-endpoint with ON CONFLICT and upserts cursor state
  - Loader persists the newest event timestamp as high-water mark
  - Pipeline wires source → destination

All DB and API interactions are mocked (unittest.mock), matching the
repo's existing test style (see tests/ingestion/test_pipeline_bugs.py).
"""

from datetime import datetime
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def _page(items, next_path=None):
    return {"items": items, "nextPagePath": next_path}


def _async_gen(pages):
    async def _gen(*_args, **_kwargs):
        for page in pages:
            yield page
    return _gen


# ---------------------------------------------------------------------------
# Source
# ---------------------------------------------------------------------------


class TestSourcePagination:

    def _build_source(self, paginated_factory, stored_ts=None):
        from pipelines.application.runners.pipeline_bronze_t212_history import (
            Trading212HistorySource,
        )

        with patch.object(Trading212HistorySource, "__init__", lambda self: None):
            source = Trading212HistorySource()
        source._api_client = MagicMock()
        source._api_client.get_paginated = paginated_factory
        source._db_client = MagicMock()
        source._get_stored_high_water_mark = MagicMock(return_value=stored_ts)
        return source

    def test_follows_next_page_path_until_null(self):
        pages_by_endpoint = {
            "equity/history/dividends": [
                _page(
                    [{"reference": "d1", "paidOn": "2026-04-19T12:00:00Z"}],
                    next_path="/api/v0/equity/history/dividends?cursor=111",
                ),
                _page(
                    [{"reference": "d2", "paidOn": "2026-04-18T12:00:00Z"}],
                    next_path=None,
                ),
            ],
            "equity/history/orders": [
                _page(
                    [{"order": {"id": 1, "createdAt": "2026-04-19T09:00:00Z"}}],
                    next_path=None,
                ),
            ],
            "equity/history/transactions": [
                _page(
                    [{"reference": "t1", "dateTime": "2026-04-19T10:00:00Z"}],
                    next_path=None,
                ),
            ],
        }

        async def fake_paginated(endpoint, cursor=None, limit=50, stop_predicate=None):
            for page in pages_by_endpoint[endpoint]:
                yield page

        source = self._build_source(fake_paginated, stored_ts=None)
        result = source.extract()

        assert len(result["dividends"]) == 2
        assert [d["reference"] for d in result["dividends"]] == ["d1", "d2"]
        assert len(result["orders"]) == 1
        assert len(result["transactions"]) == 1
        assert result["cursors"]["dividends"]["last_event_ts"] == _ts("2026-04-19T12:00:00Z")

    def test_stops_at_stored_cursor(self):
        stored = _ts("2026-04-18T00:00:00Z")

        dividend_pages = [
            _page(
                [
                    {"reference": "d_new", "paidOn": "2026-04-19T12:00:00Z"},
                    {"reference": "d_old", "paidOn": "2026-04-17T12:00:00Z"},
                ],
                next_path="/api/v0/equity/history/dividends?cursor=next",
            ),
        ]
        other_pages = {
            "equity/history/orders": [],
            "equity/history/transactions": [],
        }

        async def fake_paginated(endpoint, cursor=None, limit=50, stop_predicate=None):
            if endpoint == "equity/history/dividends":
                for page in dividend_pages:
                    yield page
                    if stop_predicate and stop_predicate(page):
                        return
            else:
                for page in other_pages[endpoint]:
                    yield page

        source = self._build_source(fake_paginated, stored_ts=stored)
        result = source.extract()

        # The older item (2026-04-17) must be filtered out; only the new one kept.
        assert [d["reference"] for d in result["dividends"]] == ["d_new"]
        assert result["cursors"]["dividends"]["last_event_ts"] == _ts("2026-04-19T12:00:00Z")

    def test_isolates_endpoint_failures(self):
        async def failing_divs(endpoint, cursor=None, limit=50, stop_predicate=None):
            if endpoint == "equity/history/dividends":
                raise RuntimeError("boom")
            if endpoint == "equity/history/orders":
                yield _page(
                    [{"order": {"id": 42, "createdAt": "2026-04-19T09:00:00Z"}}],
                    next_path=None,
                )
            else:
                yield _page(
                    [{"reference": "t1", "dateTime": "2026-04-19T10:00:00Z"}],
                    next_path=None,
                )

        source = self._build_source(failing_divs, stored_ts=None)
        result = source.extract()

        assert result["dividends"] == []
        assert len(result["orders"]) == 1
        assert len(result["transactions"]) == 1


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


class TestLoader:

    def _build_loader(self):
        from pipelines.application.runners.loaders.loader_bronze_t212_history import (
            FullLoaderPostgresT212History,
        )

        with patch(
            "pipelines.application.runners.loaders.loader_bronze_t212_history.SQLModelClient"
        ) as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client_cls.return_value = mock_client
            loader = FullLoaderPostgresT212History()
        return loader, mock_client

    def test_inserts_per_table_with_on_conflict(self):
        loader, mock_client = self._build_loader()
        data = {
            "dividends": [
                {"reference": "d1", "paidOn": "2026-04-19T12:00:00Z", "amount": 1.23},
            ],
            "orders": [
                {"order": {"id": 42, "createdAt": "2026-04-19T09:00:00Z"}},
            ],
            "transactions": [
                {"reference": "t1", "dateTime": "2026-04-19T10:00:00Z"},
            ],
            "cursors": {},
        }

        loader._loader(data)

        # One execute per endpoint insert. Cursor execs skipped (cursors empty).
        executed_sqls = [call.args[0] for call in mock_client.execute.call_args_list]
        assert any("raw.t212_history_dividend" in s for s in executed_sqls)
        assert any("raw.t212_history_order" in s for s in executed_sqls)
        assert any("raw.t212_history_transaction" in s for s in executed_sqls)
        assert all("ON CONFLICT (id, ingested_date) DO NOTHING" in s
                   for s in executed_sqls if s.strip().startswith("INSERT INTO raw.t212_history_"))

    def test_upserts_cursor_with_newest_event(self):
        loader, mock_client = self._build_loader()
        newest = _ts("2026-04-19T12:00:00Z")
        data = {
            "dividends": [],
            "orders": [],
            "transactions": [],
            "cursors": {
                "dividends": {"last_cursor": "abc", "last_event_ts": newest},
            },
        }

        loader._loader(data)

        cursor_calls = [
            call for call in mock_client.execute.call_args_list
            if "raw.t212_history_cursor" in call.args[0]
        ]
        assert len(cursor_calls) == 1
        params = cursor_calls[0].kwargs["params"]
        assert params["endpoint"] == "dividends"
        assert params["last_cursor"] == "abc"
        assert params["last_event_ts"] == newest

    def test_skips_items_without_id(self):
        loader, mock_client = self._build_loader()
        data = {
            "dividends": [
                {"paidOn": "2026-04-19T12:00:00Z"},  # no reference
                {"reference": "d_ok", "paidOn": "2026-04-19T13:00:00Z"},
            ],
            "orders": [],
            "transactions": [],
            "cursors": {},
        }

        loader._loader(data)

        dividend_inserts = [
            call for call in mock_client.execute.call_args_list
            if "raw.t212_history_dividend" in call.args[0]
        ]
        assert len(dividend_inserts) == 1
        assert dividend_inserts[0].kwargs["params"]["id"] == "d_ok"


# ---------------------------------------------------------------------------
# Pipeline wiring
# ---------------------------------------------------------------------------


class TestPipelineWiring:

    def test_run_wires_source_to_destination(self):
        from pipelines.application.runners.pipeline_bronze_t212_history import (
            PipelineT212History,
        )

        extracted = {
            "dividends": [{"reference": "d1", "paidOn": "2026-04-19T12:00:00Z"}],
            "orders": [],
            "transactions": [],
            "cursors": {},
        }

        with patch.object(PipelineT212History, "__init__", lambda self: None):
            pipeline = PipelineT212History()
        pipeline._source = MagicMock()
        pipeline._source.extract.return_value = extracted
        pipeline._destination = MagicMock()

        pipeline.run()

        pipeline._source.extract.assert_called_once()
        pipeline._destination.load.assert_called_once_with(extracted)

    def test_run_skips_load_when_no_events(self):
        from pipelines.application.runners.pipeline_bronze_t212_history import (
            PipelineT212History,
        )

        with patch.object(PipelineT212History, "__init__", lambda self: None):
            pipeline = PipelineT212History()
        pipeline._source = MagicMock()
        pipeline._source.extract.return_value = {
            "dividends": [],
            "orders": [],
            "transactions": [],
            "cursors": {},
        }
        pipeline._destination = MagicMock()

        pipeline.run()

        pipeline._destination.load.assert_not_called()
