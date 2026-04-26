import logging
from pathlib import Path

import psycopg2
import psycopg2.extras

log = logging.getLogger(__name__)

_QUERIES = (
    Path(__file__).parent.parent.parent
    / "src"
    / "pipelines"
    / "infrastructure"
    / "queries"
    / "strategies"
    / "autobuy_budget.sql"
)

# ---------------------------------------------------------------------------
# SQL loading — mirrors src/shared/database/query_loader.py
# ---------------------------------------------------------------------------


def _load_query(name: str) -> str:
    """Extract a named query block from autobuy_budget.sql."""
    sql_text = _QUERIES.read_text()
    blocks: dict[str, list[str]] = {}
    current: str | None = None
    for line in sql_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("-- name:"):
            current = stripped.split("-- name:", 1)[1].strip()
            blocks[current] = []
        elif current is not None and not stripped.startswith("--"):
            blocks[current].append(line)
    if name not in blocks:
        raise KeyError(f"Query '{name}' not found in {_QUERIES}")
    return "\n".join(blocks[name]).strip()


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------


def open_connection(database_url: str):
    return psycopg2.connect(database_url)


# ---------------------------------------------------------------------------
# Budget persistence (replaces state.json)
# ---------------------------------------------------------------------------


def get_monthly_spent(conn, month: str) -> float:
    """Return cumulative GBP spent in *month* (YYYY-MM), or 0.0 if no row."""
    sql = _load_query("get_budget")
    with conn.cursor() as cur:
        cur.execute(sql, {"month": month})
        row = cur.fetchone()
    if row is None:
        return 0.0
    return float(row[0])


def save_monthly_spent(conn, month: str, spent: float) -> None:
    """Upsert the cumulative spend total for *month*."""
    sql = _load_query("upsert_budget")
    with conn.cursor() as cur:
        cur.execute(sql, {"month": month, "spent": spent})
    conn.commit()


# ---------------------------------------------------------------------------
# Portfolio data queries
# ---------------------------------------------------------------------------


def get_drawdown(conn, tickers: list[str]) -> dict[str, float | None]:
    """Return {ticker: price_drawdown_pct_14d} for each ticker.

    Value is a negative fraction (e.g. -0.07 = 7% below 14-day high).
    NULL means the ticker has fewer than 14 rows in the gold layer.
    """
    sql = _load_query("get_drawdown")
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, {"tickers": tickers})
        rows = cur.fetchall()

    result: dict[str, float | None] = {t: None for t in tickers}
    for row in rows:
        result[row["ticker"]] = (
            float(row["price_drawdown_pct_14d"]) if row["price_drawdown_pct_14d"] is not None else None
        )

    missing = [t for t in tickers if t not in {r["ticker"] for r in rows}]
    if missing:
        log.warning("No gold-layer data found for tickers: %s", missing)

    return result


def get_cash_available(conn) -> float:
    """Return most recent cash_available_to_trade from staging.account."""
    sql = _load_query("get_cash")
    with conn.cursor() as cur:
        cur.execute(sql)
        row = cur.fetchone()

    if row is None:
        log.warning("No account row found in staging.account; defaulting cash to 0")
        return 0.0
    return float(row[0])
