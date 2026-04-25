"""
Drawdown-based auto-buy scheduler.

Run normally (scheduled):
    python scheduler.py

Run once immediately (for testing):
    python scheduler.py --run-now
"""

import argparse
import logging
import sys
from datetime import datetime, time as dtime

import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

import config
from budget import MonthlyBudget
from db import open_connection
from strategy import TrancheState, run_check
from t212_client import T212Client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

LONDON = pytz.timezone("Europe/London")
_MARKET_OPEN = dtime(9, 30)
_MARKET_CLOSE = dtime(16, 0)

_state = TrancheState()
_budget = MonthlyBudget(config.MONTHLY_LIMIT)
_client = T212Client(config.API_URL, config.API_TOKEN, config.SECRET_TOKEN)


def is_market_open() -> bool:
    now = datetime.now(LONDON)
    if now.weekday() >= 5:
        return False
    return _MARKET_OPEN <= now.time() < _MARKET_CLOSE


def job() -> None:
    if not is_market_open():
        log.info("Market closed — skipping check")
        return

    log.info("Running drawdown check")
    conn = open_connection(config.DATABASE_URL)
    try:
        run_check(conn, _client, _state, _budget, dry_run=config.DRY_RUN)
    finally:
        conn.close()


def _reset_state() -> None:
    _state.reset()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-now", action="store_true", help="Run once immediately then exit")
    args = parser.parse_args()

    if args.run_now:
        log.info("--run-now: executing job immediately")
        job()
        return

    scheduler = BlockingScheduler(timezone=LONDON)

    scheduler.add_job(job, CronTrigger(hour=9, minute=45, timezone=LONDON), id="check_morning")
    scheduler.add_job(job, CronTrigger(hour=14, minute=30, timezone=LONDON), id="check_afternoon")
    scheduler.add_job(_reset_state, CronTrigger(hour=0, minute=0, timezone=LONDON), id="daily_reset")

    log.info(
        "Scheduler started — jobs at 09:45 and 14:30 London time%s",
        " [DRY RUN]" if config.DRY_RUN else "",
    )
    scheduler.start()


if __name__ == "__main__":
    main()
