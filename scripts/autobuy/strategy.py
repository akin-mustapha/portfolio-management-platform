import logging
from dataclasses import dataclass, field
from typing import Optional

from budget import MonthlyBudget
from config import Asset, Tranche, ASSETS, MONTHLY_LIMIT
from db import get_drawdown, get_cash_available
from t212_client import T212Client

log = logging.getLogger(__name__)


@dataclass
class TrancheState:
    triggered: dict[str, set[float]] = field(default_factory=dict)

    def reset(self) -> None:
        """Clear all triggered tranches for a new trading day."""
        self.triggered.clear()
        log.info("Tranche state reset for new trading day")

    def is_triggered(self, ticker: str, drawdown_pct: float) -> bool:
        """Check whether a tranche threshold has already fired today.

        Args:
            ticker: Asset ticker symbol.
            drawdown_pct: Tranche threshold as a positive percentage (e.g. 5.0).

        Returns:
            True if the tranche was already triggered today.
        """
        return drawdown_pct in self.triggered.get(ticker, set())

    def mark_triggered(self, ticker: str, drawdown_pct: float) -> None:
        """Record that a tranche has fired so it won't fire again today.

        Args:
            ticker: Asset ticker symbol.
            drawdown_pct: Tranche threshold as a positive percentage (e.g. 5.0).
        """
        self.triggered.setdefault(ticker, set()).add(drawdown_pct)


def _deepest_untriggered(
    ticker: str,
    drawdown_pct: float,
    tranches: tuple[Tranche, ...],
    state: TrancheState,
) -> Optional[Tranche]:
    """Return the highest-threshold tranche that is breached and not yet triggered.

    Args:
        ticker: Asset ticker symbol.
        drawdown_pct: Current drawdown as a positive percentage (e.g. 7.0 = 7% below high).
        tranches: Ordered tranche definitions for this asset.
        state: In-memory record of which tranches have already fired today.

    Returns:
        The deepest eligible Tranche, or None if no tranche should fire.
    """
    candidates = [
        t for t in tranches
        if drawdown_pct >= t.drawdown_pct and not state.is_triggered(ticker, t.drawdown_pct)
    ]
    return max(candidates, key=lambda t: t.drawdown_pct) if candidates else None


def run_check(
    conn,
    client: T212Client,
    state: TrancheState,
    budget: MonthlyBudget,
    dry_run: bool = False,
) -> None:
    """Evaluate drawdown for all watched assets and place tranche orders where due.

    Reads current drawdown from the gold layer, checks available cash and the monthly
    budget cap, then places the deepest untriggered tranche for each asset that has
    breached a threshold. Both cash and monthly spend are tracked across the loop so
    subsequent assets see the updated figures.

    Args:
        conn: Open psycopg2 connection to the portfolio database.
        client: Authenticated Trading212 API client.
        state: In-memory tranche trigger state for the current trading day.
        budget: Persistent monthly spend tracker.
        dry_run: When True, log intended orders but skip the API call.
    """
    tickers = [a.ticker for a in ASSETS]
    drawdowns = get_drawdown(conn, tickers)
    cash = get_cash_available(conn)
    log.info("Cash available: £%.2f | Monthly remaining: £%.2f / £%.2f",
             cash, budget.remaining, budget.limit)

    asset_map: dict[str, Asset] = {a.ticker: a for a in ASSETS}

    for ticker, raw_drawdown in drawdowns.items():
        if raw_drawdown is None:
            log.warning("SKIP | ticker=%s | reason=no 14-day drawdown data yet", ticker)
            continue

        # price_drawdown_pct_14d is a negative fraction; convert to positive %
        drawdown_pct = abs(raw_drawdown) * 100
        asset = asset_map[ticker]

        tranche = _deepest_untriggered(ticker, drawdown_pct, asset.tranches, state)
        if tranche is None:
            log.info("ticker=%s | drawdown=%.2f%% | no tranche triggered", ticker, drawdown_pct)
            continue

        if cash < tranche.order_value:
            log.warning(
                "SKIP | ticker=%s | reason=insufficient cash | available=£%.2f | required=£%.2f",
                ticker, cash, tranche.order_value,
            )
            continue

        if not budget.can_spend(tranche.order_value):
            log.warning(
                "SKIP | ticker=%s | reason=monthly limit reached | remaining=£%.2f | required=£%.2f",
                ticker, budget.remaining, tranche.order_value,
            )
            continue

        if dry_run:
            log.info(
                "DRY RUN | ticker=%s | drawdown=%.2f%% | tranche=£%.2f",
                ticker, drawdown_pct, tranche.order_value,
            )
            state.mark_triggered(ticker, tranche.drawdown_pct)
            continue

        try:
            response = client.place_market_order(ticker, tranche.order_value)
            log.info(
                "ORDER PLACED | ticker=%s | drawdown=%.2f%% | tranche=£%.2f | response=%s",
                ticker, drawdown_pct, tranche.order_value, response,
            )
            state.mark_triggered(ticker, tranche.drawdown_pct)
            budget.record(tranche.order_value)
            cash -= tranche.order_value
        except Exception as exc:
            log.error("ORDER FAILED | ticker=%s | error=%s", ticker, exc)
