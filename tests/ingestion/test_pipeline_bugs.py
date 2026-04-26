"""
Tests that expose known bugs in the silver and gold pipeline layer.

Each test class documents one bug:
  - Why the bug matters
  - What the test checks
  - What the fix should be

Tests are written to FAIL before the fix and PASS after.
"""

import inspect
from datetime import datetime
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# Bug 3: pipeline_account_gold.py — SQL starts with ";WITH" (leading semicolon)
# ---------------------------------------------------------------------------


class TestBug3AccountGoldLeadingSemicolon:
    """
    Bug: AccountGoldSource.extract() contained a leading semicolon before WITH.

    The canonical gold pipeline is now PipelineT212Gold (pipeline_gold_t212.py)
    which uses T212GoldSource — a single unified source for both asset and account
    facts. These tests verify the SQL in T212GoldSource has no leading semicolon.
    """

    def test_account_gold_sql_has_no_leading_semicolon(self):
        """
        The SQL must not contain the ';WITH' pattern.
        """
        from pipelines.application.runners.pipeline_gold_t212 import (
            T212GoldSource,
        )

        src = inspect.getsource(T212GoldSource.extract)
        assert ";WITH" not in src, (
            "SQL contains ';WITH' which is a syntax error in PostgreSQL. The query should begin with 'WITH'."
        )

    def test_account_gold_sql_starts_with_valid_cte(self):
        """
        Complementary check: the SQL must not have a leading semicolon before WITH.
        """
        from pipelines.application.runners.pipeline_gold_t212 import (
            T212GoldSource,
        )

        src = inspect.getsource(T212GoldSource.extract)
        assert '";WITH' not in src and "';WITH" not in src and "\n            ;WITH" not in src, (
            "SQL has a leading ';' before WITH — this is a syntax error. Remove the semicolon."
        )


# ---------------------------------------------------------------------------
# Bug 4: policies.py — FullLoader._loader abstract method missing 'data' param
# ---------------------------------------------------------------------------


class TestBug4FullLoaderAbstractMethodSignature:
    """
    Bug: FullLoader.load(self, data) calls self._loader(data) with a positional
    argument, but the abstract method is declared as:

        @abstractmethod
        def _loader(self):
            pass

    Missing the 'data' parameter. The abstract contract is wrong — subclasses
    that correctly implement _loader(self, data) have a different signature than
    what the abstract declaration says.

    If a subclass naively follows the abstract method signature and implements
    _loader(self) without data, calling load() raises TypeError because
    self._loader(data) passes an unexpected positional argument.

    Fix: change the abstract method to _loader(self, data).
    """

    def test_full_loader_abstract_loader_has_data_parameter(self):
        """
        The abstract _loader method must declare a 'data' parameter to match
        how it is called inside load().
        FAILS before fix (param missing), PASSES after fix.
        """
        from pipelines.application.policies import FullLoader

        sig = inspect.signature(FullLoader._loader)
        params = list(sig.parameters.keys())

        assert "data" in params, (
            f"FullLoader._loader abstract method is missing the 'data' parameter. "
            f"Got: {params}. It is called as self._loader(data) inside load(), "
            f"so the contract must declare that parameter."
        )

    def test_concrete_full_loader_without_data_param_raises_on_load(self):
        """
        A subclass that follows the (broken) abstract signature — implementing
        _loader(self) without 'data' — raises TypeError when load() is called,
        because load() passes the data argument.

        After the fix, the abstract signature makes the contract explicit and
        this scenario should never occur.
        """
        from pipelines.application.policies import FullLoader

        class BrokenLoader(FullLoader):
            """Implements the broken abstract signature (no data param)."""

            def _create_partition(self):
                pass

            def _loader(self):  # missing data param — follows broken abstract contract
                pass

        loader = BrokenLoader("test_table")

        with pytest.raises(TypeError):
            loader.load(["record1"])  # load() calls self._loader(data) → TypeError

    def test_concrete_full_loader_with_data_param_works(self):
        """
        A correct subclass implementation (with data param) must work end-to-end.
        This is the post-fix expected behaviour.
        """
        from pipelines.application.policies import FullLoader

        received = []

        class CorrectLoader(FullLoader):
            def _create_partition(self):
                pass

            def _loader(self, data):
                received.extend(data)

        loader = CorrectLoader("test_table")
        loader.load(["record1", "record2"])

        assert received == ["record1", "record2"]


# ---------------------------------------------------------------------------
# Bug 5: pipeline_silver_t212.py — position_data / account_data returned as
#         JSON string instead of Python object after session closes
# ---------------------------------------------------------------------------


class TestBug5T212SilverJsonbReturnedAsString:
    """
    Bug: Trading212AssetTransformationSilver.transform() at line 67:

        positions = row.position_data  # psycopg2 deserialises JSONB → Python list

    The comment is optimistic. SQLModelClient.execute() closes the session
    before result.fetchall() is called (fetchall() is invoked outside the
    'with self._client' block). Under this pattern, JSONB columns can come
    back as raw JSON strings rather than deserialized Python objects.

    When positions is a string '[{"instrument": {...}}]', iterating over it
    yields individual characters. pos.get("instrument", {}) then raises:
        AttributeError: 'str' object has no attribute 'get'

    Fix: add json.loads() guard in both asset and account transforms.
    """

    def _make_asset_row(self, position_data):
        row = MagicMock()
        row.snapshot_id = "snap-001"
        row.ingested_timestamp = datetime(2024, 1, 1, 12, 0, 0)
        row.position_data = position_data
        return row

    def test_transform_raises_when_position_data_is_json_string(self):
        """
        Demonstrates the bug: position_data as a raw JSON string causes
        AttributeError because iterating over a str yields characters.

        FAILS (raises AttributeError) before the fix.
        PASSES (returns 1 record) after the fix.
        """
        import json

        from pipelines.application.runners.pipeline_silver_t212 import (
            Trading212AssetTransformationSilver,
        )

        position_list = [
            {
                "instrument": {
                    "ticker": "AAPL_EQ",
                    "name": "Apple Inc",
                    "currency": "USD",
                },
                "quantity": 10.0,
                "currentPrice": 150.0,
                "averagePricePaid": 130.0,
                "quantityInPies": 0.0,
                "walletImpact": {
                    "currency": "GBP",
                    "currentValue": 1500.0,
                    "totalCost": 1300.0,
                    "unrealizedProfitLoss": 200.0,
                    "fxImpact": 5.0,
                },
            }
        ]

        # Simulate JSONB coming back as a JSON string (the bug scenario)
        row = self._make_asset_row(position_data=json.dumps(position_list))

        result = Trading212AssetTransformationSilver().transform([row])
        assert len(result) == 1
        assert result[0]["ticker"] == "AAPL"

    def test_transform_happy_path_with_python_list(self):
        """
        Happy path: position_data is a Python list (standard psycopg2 behavior).
        Returns correctly shaped records.
        Passes before and after the fix.
        """
        from pipelines.application.runners.pipeline_silver_t212 import (
            Trading212AssetTransformationSilver,
        )

        row = self._make_asset_row(
            position_data=[
                {
                    "instrument": {
                        "ticker": "AAPL_EQ",
                        "name": "Apple Inc",
                        "currency": "USD",
                    },
                    "quantity": 10.0,
                    "currentPrice": 150.0,
                    "averagePricePaid": 130.0,
                    "quantityInPies": 0.0,
                    "walletImpact": {
                        "currency": "GBP",
                        "currentValue": 1500.0,
                        "totalCost": 1300.0,
                        "unrealizedProfitLoss": 200.0,
                        "fxImpact": 5.0,
                    },
                }
            ]
        )

        result = Trading212AssetTransformationSilver().transform([row])

        assert len(result) == 1
        assert result[0]["ticker"] == "AAPL"
        assert result[0]["external_id"] == "AAPL_EQ"
        assert result[0]["snapshot_id"] == "snap-001"

    def test_non_dict_entries_in_positions_go_to_parse_errors(self):
        """
        Real-world case: position_data list contains a bare string like 'error'
        mixed in with valid position dicts (observed in live T212 data).

        The valid dict must be processed normally; the string entry must be
        captured in _parse_errors (for dead letter) and skipped — not raise
        AttributeError.
        """
        from pipelines.application.runners.pipeline_silver_t212 import (
            Trading212AssetTransformationSilver,
        )

        valid_position = {
            "instrument": {"ticker": "AAPL_EQ", "name": "Apple Inc", "currency": "USD"},
            "quantity": 10.0,
            "currentPrice": 150.0,
            "averagePricePaid": 130.0,
            "quantityInPies": 0.0,
            "walletImpact": {
                "currency": "GBP",
                "currentValue": 1500.0,
                "totalCost": 1300.0,
                "unrealizedProfitLoss": 200.0,
                "fxImpact": 5.0,
            },
        }

        row = self._make_asset_row(position_data=[valid_position, "error", valid_position])

        transform = Trading212AssetTransformationSilver()
        result = transform.transform([row])

        # Valid positions processed
        assert len(result) == 2
        assert all(r["ticker"] == "AAPL" for r in result)

        # Bad entry captured for dead letter
        assert len(transform._parse_errors) == 1
        assert transform._parse_errors[0].error_type == "InvalidPositionEntry"
        assert transform._parse_errors[0].business_key == "snap-001"
