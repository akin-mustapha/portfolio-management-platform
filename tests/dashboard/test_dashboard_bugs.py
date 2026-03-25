"""
Tests that expose known bugs in the dashboard layer.

Each test class documents one bug:
  - Why the bug matters
  - What the test checks
  - What the fix should be

Tests are written to FAIL before the fix and PASS after.
"""

import inspect
import pytest


# ---------------------------------------------------------------------------
# Bug 1: workspace_tabs.py — risk_tab_content() and opportunities_tab_content()
#         called without view_model or theme arguments
# ---------------------------------------------------------------------------


class TestBug1WorkspaceTabsMissingArgs:
    """
    Bug: workspace_tabs() passes view_model and theme to portfolio_tab_content()
    correctly, but calls risk_tab_content() and opportunities_tab_content()
    with no arguments:

        children=risk_tab_content(),          # line 40 — BUG
        children=opportunities_tab_content(), # line 47 — BUG

    Both functions default view_model=None and immediately return a loading
    placeholder when view_model is None. This means the Risk and Opportunities
    tabs ALWAYS show "Loading…" regardless of whether data has been fetched.

    Fix: pass view_model and theme to both calls, matching portfolio_tab_content.
    """

    def test_workspace_tabs_source_passes_view_model_to_risk_tab(self):
        """
        The source of workspace_tabs() must call risk_tab_content with
        view_model as an argument, not as a bare zero-argument call.
        FAILS before fix ('risk_tab_content()' present), PASSES after fix.
        """
        from dashboard.pages.portfolio.components.organisms.workspace_tabs import (
            workspace_tabs,
        )
        src = inspect.getsource(workspace_tabs)
        assert "risk_tab_content()" not in src, (
            "workspace_tabs() calls risk_tab_content() with no arguments. "
            "The Risk tab will always show 'Loading…' because view_model defaults "
            "to None. Fix: call risk_tab_content(view_model, theme)."
        )

    def test_workspace_tabs_source_passes_view_model_to_opportunities_tab(self):
        """
        The source of workspace_tabs() must call opportunities_tab_content with
        view_model as an argument, not as a bare zero-argument call.
        FAILS before fix, PASSES after fix.
        """
        from dashboard.pages.portfolio.components.organisms.workspace_tabs import (
            workspace_tabs,
        )
        src = inspect.getsource(workspace_tabs)
        assert "opportunities_tab_content()" not in src, (
            "workspace_tabs() calls opportunities_tab_content() with no arguments. "
            "The Opportunities tab will always show 'Loading…' because view_model "
            "defaults to None. Fix: call opportunities_tab_content(view_model, theme)."
        )

    def test_workspace_tabs_source_passes_view_model_to_portfolio_tab(self):
        """
        Regression guard: portfolio_tab_content was already passing view_model
        correctly. The source must still contain that correct call pattern.
        """
        from dashboard.pages.portfolio.components.organisms.workspace_tabs import (
            workspace_tabs,
        )
        src = inspect.getsource(workspace_tabs)
        assert "portfolio_tab_content(view_model" in src, (
            "portfolio_tab_content() is no longer receiving view_model — "
            "regression introduced in the fix."
        )

    def test_risk_tab_content_returns_loading_placeholder_without_view_model(self):
        """
        Regression guard: risk_tab_content(view_model=None) must still return the
        loading placeholder. This is the expected loading state.
        """
        from dashboard.pages.portfolio.tabs.tab_risk import risk_tab_content

        result = risk_tab_content(view_model=None, theme="light")
        assert getattr(result, "id", None) == "tab-risk-content", (
            "risk_tab_content(None) should return the loading placeholder."
        )

    def test_opportunities_tab_content_returns_loading_placeholder_without_view_model(self):
        """
        Regression guard: opportunities_tab_content(view_model=None) must return
        the loading placeholder.
        """
        from dashboard.pages.portfolio.tabs.tab_opportunities import (
            opportunities_tab_content,
        )

        result = opportunities_tab_content(view_model=None, theme="light")
        assert getattr(result, "id", None) == "tab-opportunities-content", (
            "opportunities_tab_content(None) should return the loading placeholder."
        )


# ---------------------------------------------------------------------------
# Bug 2: portfolio_presenter.py — _winners_pnl_vm() and _losers_pnl_vm()
#         raise KeyError when called with an empty list
# ---------------------------------------------------------------------------


class TestBug2PresenterWinnersLosersEmptyInput:
    """
    Bug: _winners_pnl_vm() and _losers_pnl_vm() in PortfolioPresenter do:

        df = pd.DataFrame(assets)
        return df[df["is_profitable"] == 1].groupby("data_date")["profit"].sum().to_dict()

    When assets=[], pd.DataFrame([]) creates an empty DataFrame with no columns.
    Indexing df["is_profitable"] raises KeyError because the column does not exist.
    The exception is re-raised bare (raise e) with no fallback, so the whole
    page load callback crashes and no data is presented.

    Fix: return {} when df is empty or missing required columns.
    """

    def test_winners_pnl_vm_returns_empty_dict_on_empty_input(self):
        """
        _winners_pnl_vm([]) must return {} instead of raising KeyError.
        FAILS before fix (raises KeyError), PASSES after fix.
        """
        from dashboard.presenters.portfolio_presenter import PortfolioPresenter

        presenter = PortfolioPresenter()
        result = presenter._winners_pnl_vm([])
        assert result == {}, (
            "_winners_pnl_vm([]) raised an exception instead of returning {}. "
            "Fix: guard against empty DataFrame before accessing 'is_profitable' column."
        )

    def test_losers_pnl_vm_returns_empty_dict_on_empty_input(self):
        """
        _losers_pnl_vm([]) must return {} instead of raising KeyError.
        FAILS before fix (raises KeyError), PASSES after fix.
        """
        from dashboard.presenters.portfolio_presenter import PortfolioPresenter

        presenter = PortfolioPresenter()
        result = presenter._losers_pnl_vm([])
        assert result == {}, (
            "_losers_pnl_vm([]) raised an exception instead of returning {}. "
            "Fix: guard against empty DataFrame before accessing 'is_profitable' column."
        )

    def test_winners_pnl_vm_returns_correct_data_when_input_is_valid(self):
        """
        When assets_history contains records, _winners_pnl_vm() must aggregate
        profit for profitable positions (is_profitable == 1) by date.
        Regression guard — valid data must still produce correct output.
        """
        from dashboard.presenters.portfolio_presenter import PortfolioPresenter

        assets_history = [
            {"data_date": "2024-01-01", "is_profitable": 1, "profit": 100.0},
            {"data_date": "2024-01-01", "is_profitable": 1, "profit": 50.0},
            {"data_date": "2024-01-01", "is_profitable": 0, "profit": -20.0},
            {"data_date": "2024-01-02", "is_profitable": 1, "profit": 80.0},
        ]

        presenter = PortfolioPresenter()
        result = presenter._winners_pnl_vm(assets_history)

        assert result["2024-01-01"] == pytest.approx(150.0)
        assert result["2024-01-02"] == pytest.approx(80.0)

    def test_losers_pnl_vm_returns_correct_data_when_input_is_valid(self):
        """
        When assets_history contains records, _losers_pnl_vm() must aggregate
        profit for unprofitable positions (is_profitable == 0) by date.
        """
        from dashboard.presenters.portfolio_presenter import PortfolioPresenter

        assets_history = [
            {"data_date": "2024-01-01", "is_profitable": 0, "profit": -30.0},
            {"data_date": "2024-01-01", "is_profitable": 1, "profit": 100.0},
            {"data_date": "2024-01-02", "is_profitable": 0, "profit": -45.0},
        ]

        presenter = PortfolioPresenter()
        result = presenter._losers_pnl_vm(assets_history)

        assert result["2024-01-01"] == pytest.approx(-30.0)
        assert result["2024-01-02"] == pytest.approx(-45.0)

    def test_present_does_not_raise_when_assets_history_is_empty(self):
        """
        The full present() call must not raise when portfolio data has no asset
        history (e.g. first run or fresh account). This exercises the full path
        from present() → _winners_pnl_vm([]) and _losers_pnl_vm([]).
        """
        from dashboard.presenters.portfolio_presenter import PortfolioPresenter

        minimal_data = {
            "portfolio_current_snapshot": {},
            "assets": [],
            "assets_history": [],
            "portfolio_history": [],
            "available_tags": [],
            "pnl": [],
        }

        presenter = PortfolioPresenter()
        result = presenter.present(minimal_data)

        assert result["winners_pnl"] == {}
        assert result["losers_pnl"] == {}


# ---------------------------------------------------------------------------
# Bug 3: portfolio_charts.py — PortfolioPerformancePlotlyLineChart.render()
#         raises IndexError when portfolio_value_series has no data points
# ---------------------------------------------------------------------------


class TestBug3PortfolioPerformanceChartEmptyData:
    """
    Bug: PortfolioPerformancePlotlyLineChart.render() does:

        df = pd.DataFrame(data).sort_values("dates")
        ref_value = df["costs"].iloc[0]   # line 655

    When data = {"dates": [], "values": [], "costs": []} (empty series — no
    portfolio history yet), df has 0 rows. df["costs"].iloc[0] raises:
        IndexError: single positional indexer is out-of-bounds

    This crashes the entire portfolio_tab_content() render, so the Valuation
    tab is completely blank on first run or for a fresh account with no history.

    Fix: guard against empty DataFrame and return an empty figure.
    """

    _EMPTY_DATA = {"dates": [], "values": [], "costs": []}

    _VALID_DATA = {
        "dates": ["2024-01-01", "2024-01-02", "2024-01-03"],
        "values": [1000.0, 1050.0, 1020.0],
        "costs": [900.0, 900.0, 900.0],
    }

    def test_render_does_not_raise_on_empty_data(self):
        """
        render() with empty series must return a Figure without raising IndexError.
        FAILS before fix (raises IndexError), PASSES after fix.
        """
        from dashboard.pages.portfolio.charts.portfolio_charts import (
            PortfolioPerformancePlotlyLineChart,
        )

        chart = PortfolioPerformancePlotlyLineChart()
        # Must not raise
        fig = chart.render(self._EMPTY_DATA, theme="light")
        assert fig is not None, "render() returned None instead of an empty Figure"

    def test_render_returns_valid_figure_on_empty_data(self):
        """
        The returned figure on empty data must be a plotly Figure object
        so Dash can display it (even if it shows no traces).
        """
        import plotly.graph_objects as go
        from dashboard.pages.portfolio.charts.portfolio_charts import (
            PortfolioPerformancePlotlyLineChart,
        )

        chart = PortfolioPerformancePlotlyLineChart()
        fig = chart.render(self._EMPTY_DATA, theme="light")
        assert isinstance(fig, go.Figure)

    def test_render_produces_correct_chart_with_valid_data(self):
        """
        Regression guard: render() with real data must still produce a Figure
        with the expected traces (Invested + Portfolio Value).
        """
        import plotly.graph_objects as go
        from dashboard.pages.portfolio.charts.portfolio_charts import (
            PortfolioPerformancePlotlyLineChart,
        )

        chart = PortfolioPerformancePlotlyLineChart()
        fig = chart.render(self._VALID_DATA, theme="light")

        assert isinstance(fig, go.Figure)
        # Must have at least the Portfolio Value trace and Invested trace
        trace_names = [t.name for t in fig.data]
        assert "Portfolio Value" in trace_names
        assert "Invested" in trace_names
