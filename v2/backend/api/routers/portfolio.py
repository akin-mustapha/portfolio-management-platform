from fastapi import APIRouter, Query

from backend.application.portfolio.factory import build_portfolio_service
from backend.api.serialization import date_response

router = APIRouter(tags=["portfolio"])


@router.get("/portfolio/summary")
def get_portfolio_summary():
    """
    Full portfolio snapshot: KPIs, asset table, all chart series, available tags.
    """
    return date_response(build_portfolio_service().get_portfolio_summary())


@router.get("/portfolio/history")
def get_portfolio_history(
    from_date: str = Query(None, alias="from"),
    to_date: str = Query(None, alias="to"),
):
    """
    Portfolio daily history series, optionally filtered by date range.
    """
    rows = build_portfolio_service().get_portfolio_history(from_date, to_date)
    return date_response(rows)
