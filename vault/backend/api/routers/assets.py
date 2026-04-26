import datetime

from fastapi import APIRouter, Query

from backend.api.serialization import date_response
from backend.application.portfolio.factory import build_portfolio_service

router = APIRouter(tags=["assets"])

_DEFAULT_HISTORY_DAYS = 90


def _default_date_range():
    today = datetime.date.today()
    start = today - datetime.timedelta(days=_DEFAULT_HISTORY_DAYS)
    return str(start), str(today)


@router.get("/assets")
def get_assets(
    tags: str = Query(None, description="Comma-separated tag names to filter"),
):
    """
    Most recent asset data row per ticker, with price_series and tags attached.
    Optional ?tags=tag1,tag2 filter (server-side, case-insensitive).
    """
    rows = build_portfolio_service().get_most_recent_assets(tag_filter=tags)
    return date_response(rows)


@router.get("/assets/{ticker}/history")
def get_asset_history(
    ticker: str,
    from_date: str = Query(None, alias="from"),
    to_date: str = Query(None, alias="to"),
):
    """
    Per-asset time-series data.
    """
    default_start, default_end = _default_date_range()
    start = from_date or default_start
    end = to_date or default_end

    rows = build_portfolio_service().get_asset_history(ticker.upper(), start, end)
    return date_response(rows)


@router.get("/assets/{ticker}/profile")
def get_asset_profile(ticker: str):
    """
    Asset profile metadata: tags, industries, sectors, categories for a given ticker.
    Uses the most-recent asset row from the analytics layer.
    """
    profile = build_portfolio_service().get_asset_profile(ticker.upper())
    if profile is None:
        return date_response({"error": f"Asset '{ticker}' not found"})
    return date_response(profile)
