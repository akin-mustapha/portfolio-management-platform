"""
Tests that expose known bugs in the silver and gold pipeline layer.

Each test class documents one bug:
  - Why the bug matters
  - What the test checks
  - What the fix should be

Tests are written to FAIL before the fix and PASS after.
"""

import inspect
import pandas as pd
import pytest
from datetime import datetime
from unittest.mock import MagicMock


# ---------------------------------------------------------------------------
# Bug 1: pipeline_asset_silver.py — rename() called without columns= kwarg
#         and result is not assigned (complete dead code)
# ---------------------------------------------------------------------------

class TestBug1AssetSilverRenameDeadCode:
    """
    Bug: Trading212AssetTransformationSilver.transform() (line 82-84) calls

        bronze_asset_df.rename({"ticker": "external_id"})

    This is wrong in two ways:
    1. pandas.DataFrame.rename() without `columns=` treats the dict as an
       index (row-label) mapper, not a column mapper — so no column is renamed.
    2. The return value is not assigned back, so even if the rename were
       column-targeted it would be silently discarded.

    The column rename is entirely a no-op. The pipeline still produces
    correct output only because external_id is manually re-assigned on
    the very next line (asset_df["external_id"] = df["ticker"]).

    Fix: remove the dead rename call entirely.
    """

    def test_rename_without_columns_kwarg_is_a_noop_on_columns(self):
        """
        Show that the exact code in the pipeline leaves column names unchanged.
        After the fix (dead code removed) this test remains green because the
        problematic line no longer exists.
        """
        df = pd.DataFrame({"ticker": ["AAPL_EQ"]})
        # This is what the code currently does — no columns= kwarg, result ignored
        df.rename({"ticker": "external_id"})
        # Column is NOT renamed
        assert "ticker" in df.columns
        assert "external_id" not in df.columns

    def test_asset_silver_transformation_external_id_is_correct(self):
        """
        End-to-end: external_id must equal the raw ticker value from the source
        (the full Trading212 ticker string, e.g. "AAPL_EQ").
        This passes before and after the fix because external_id is assigned
        directly — but ensures the rename bug has no side-effect on output.
        """
        from pipelines.application.runners.pipeline_asset_silver import (
            Trading212AssetTransformationSilver,
        )

        data = [
            {
                "ticker": "AAPL_EQ",
                "instrument_name": "Apple Inc",
                "instrument_currency": "USD",
                "wallet_currency": "GBP",
                "quantity": 10.0,
                "current_price": 150.0,
                "average_price_paid": 130.0,
                "current_value": 1500.0,
                "total_cost": 1300.0,
                "unrealized_pnl": 200.0,
                "fx_impact": 5.0,
                "quantity_in_pies": 0.0,
                "business_key": "AAPL_EQ_2024-01-01",
                "ingested_timestamp": datetime(2024, 1, 1),
            }
        ]

        result = Trading212AssetTransformationSilver().transform(data)

        assert len(result) == 1
        # external_id must be the full Trading212 ticker (before the "_" split)
        assert result[0]["external_id"] == "AAPL_EQ"
        # ticker must be the prefix only
        assert result[0]["ticker"] == "AAPL"

    def test_asset_silver_transform_source_code_has_no_dead_rename(self):
        """
        After the fix, the dead rename call must be absent from the source.
        FAILS before fix (line exists), PASSES after fix (line removed).
        """
        from pipelines.application.runners.pipeline_asset_silver import (
            Trading212AssetTransformationSilver,
        )
        src = inspect.getsource(Trading212AssetTransformationSilver.transform)
        # The broken pattern: rename called without columns= on a result that's discarded
        assert 'bronze_asset_df.rename({' not in src, (
            "Dead rename() call found. Remove it — it renames index labels, not columns, "
            "and the return value is discarded. external_id is already assigned directly."
        )


# ---------------------------------------------------------------------------
# Bug 2: pipeline_asset_computed_silver.py — WHERE clause prevents metric
#         updates after the first pipeline run
# ---------------------------------------------------------------------------

class TestBug2AssetComputedWhereClausePreventsUpdates:
    """
    Bug: Trading212AssetComputedSourceSilver.extract() ends with:

        WHERE s.asset_id NOT IN (SELECT asset_id FROM staging.asset_computed)

    After the first pipeline run, staging.asset_computed contains a row for
    every asset_id that was processed. On ALL subsequent runs the source
    returns 0 records — so computed metrics (daily_return, moving averages,
    drawdown, var_95_1d, etc.) are NEVER refreshed.

    Fix: remove the WHERE filter. The UPSERT in the destination handles
    idempotency — existing rows are updated with fresh metric values.
    """

    def test_where_clause_is_absent_from_source_sql(self):
        """
        After the fix, the SQL must not contain the NOT IN filter that freezes
        metrics after the first run.
        FAILS before fix (clause present), PASSES after fix (clause removed).
        """
        from pipelines.application.runners.pipeline_asset_computed_silver import (
            Trading212AssetComputedSourceSilver,
        )
        src = inspect.getsource(Trading212AssetComputedSourceSilver.extract)
        assert "NOT IN (SELECT asset_id FROM staging.asset_computed)" not in src, (
            "The WHERE NOT IN filter prevents asset computed metrics from being "
            "refreshed after the first pipeline run. Remove it — the UPSERT in "
            "Trading212AssetComputedDestination handles idempotency."
        )

    def test_pipeline_run_loads_data_when_source_returns_records(self):
        """
        When the source returns records the pipeline must load them.
        This is a regression guard: verifies run() does not silently skip data.
        """
        from pipelines.application.runners.pipeline_asset_computed_silver import (
            PipelineAssetComputedSilver,
            AssetComputed,
        )

        pipeline = PipelineAssetComputedSilver.__new__(PipelineAssetComputedSilver)

        asset_computed_record = AssetComputed(
            asset_id="test-uuid",
            cost_basis=1000.0,
            daily_return=0.01,
            cumulative_return=0.05,
            dca_bias=1.1,
            pct_drawdown=-0.02,
            recent_value_high_30d=1100.0,
            recent_value_low_30d=900.0,
            recent_profit_high_30d=100.0,
            recent_profit_low_30d=-50.0,
            value_high=1200.0,
            value_low=800.0,
            ma_20d=1050.0,
            ma_30d=1020.0,
            ma_50d=990.0,
            volatility_20d=0.015,
            volatility_30d=0.018,
            volatility_50d=0.020,
            pnl_pct=10.0,
            var_95_1d=25.0,
            profit_range_30d=150.0,
            ma_crossover_signal=60.0,
            position_weight_pct=5.0,
        )

        mock_source = MagicMock()
        mock_transformation = MagicMock()
        mock_destination = MagicMock()

        mock_source.extract.return_value = [MagicMock()]
        mock_transformation.transform.return_value = [asset_computed_record]

        pipeline._source = mock_source
        pipeline._transformation = mock_transformation
        pipeline._destination = mock_destination

        pipeline.run()

        mock_destination.load.assert_called_once()
        # load(data) is called with a positional arg — access via call_args[0][0]
        loaded_records = mock_destination.load.call_args[0][0]
        assert len(loaded_records) == 1
        assert loaded_records[0]["asset_id"] == "test-uuid"


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
            "SQL contains ';WITH' which is a syntax error in PostgreSQL. "
            "The query should begin with 'WITH'."
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
            "SQL has a leading ';' before WITH — this is a syntax error. "
            "Remove the semicolon."
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

        row = self._make_asset_row(position_data=[
            {
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
        ])

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
