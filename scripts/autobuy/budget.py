import logging
from datetime import date

from db import get_monthly_spent, open_connection, save_monthly_spent

log = logging.getLogger(__name__)


class MonthlyBudget:
    """Tracks combined spend against a monthly GBP cap, persisted in staging.autobuy_budget.

    On load, the stored spend for the current calendar month is fetched from Postgres.
    A new month always starts at zero (no row exists yet).

    Args:
        limit: Maximum combined GBP spend allowed in a calendar month.
    """

    def __init__(self, limit: float) -> None:
        import config  # local import avoids circular dependency at module level

        self.limit = limit
        self._database_url = config.DATABASE_URL
        self._month: str = self._current_month()
        self._spent: float = self._load()
        log.info("Monthly spend loaded: £%.2f / £%.2f", self._spent, self.limit)

    # ------------------------------------------------------------------
    # Public interface — unchanged
    # ------------------------------------------------------------------

    @property
    def spent(self) -> float:
        return self._spent

    @property
    def remaining(self) -> float:
        return max(self.limit - self._spent, 0.0)

    def can_spend(self, amount: float) -> bool:
        return self._spent + amount <= self.limit

    def record(self, amount: float) -> None:
        self._spent += amount
        conn = open_connection(self._database_url)
        try:
            save_monthly_spent(conn, self._month, self._spent)
        finally:
            conn.close()
        log.info("Monthly spend: £%.2f / £%.2f", self._spent, self.limit)

    # ------------------------------------------------------------------

    def _current_month(self) -> str:
        return date.today().strftime("%Y-%m")

    def _load(self) -> float:
        conn = open_connection(self._database_url)
        try:
            return get_monthly_spent(conn, self._month)
        finally:
            conn.close()
