from fastapi import APIRouter, Query
from legacy.dashboard.controllers.asset_controller import AssetController
from legacy.dashboard.infrastructure.repositories.repository_factory import (
    RepositoryFactory,
)
from api.serialization import date_response
import datetime

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
    repo = RepositoryFactory.get("asset_analytics")
    raw = repo.get_most_recent_asset_data()
    rows = [dict(r._mapping) for r in raw]

    if tags:
        requested = {t.strip().lower() for t in tags.split(",") if t.strip()}
        tag_rows_raw = repo.get_asset_tags()
        tag_map: dict[str, list[str]] = {}
        for r in tag_rows_raw:
            row = dict(r._mapping)
            tag_map.setdefault(row["ticker"].upper(), []).append(row["tag_name"])
        rows = [
            r
            for r in rows
            if requested & {t.lower() for t in tag_map.get(r["ticker"].upper(), [])}
        ]

    return date_response(rows)


@router.get("/assets/{ticker}/history")
def get_asset_history(
    ticker: str,
    from_date: str = Query(None, alias="from"),
    to_date: str = Query(None, alias="to"),
):
    """
    Per-asset time-series data.  Delegates to AssetController → AssetPresenter.
    """
    default_start, default_end = _default_date_range()
    start = from_date or default_start
    end = to_date or default_end

    vm = AssetController().get_asset_snapshot(ticker.upper(), start, end)
    return date_response(vm)


@router.get("/assets/{ticker}/profile")
def get_asset_profile(ticker: str):
    """
    Asset profile metadata: tags, industries, sectors, categories for a given ticker.
    Uses the most-recent asset row from the analytics layer.
    """
    repo = RepositoryFactory.get("asset_analytics")
    raw = repo.get_most_recent_asset_data()
    rows = [dict(r._mapping) for r in raw]
    asset_row = next((r for r in rows if r["ticker"].upper() == ticker.upper()), None)
    if asset_row is None:
        return date_response({"error": f"Asset '{ticker}' not found"})

    from legacy.dashboard.controllers.asset_profile_controller import (
        AssetProfileController,
    )

    profile = AssetProfileController().get_profile(asset_row)
    return date_response(profile)
