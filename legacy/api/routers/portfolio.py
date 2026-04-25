from fastapi import APIRouter, Query
from legacy.dashboard.controllers.portfolio_controller import PortfolioController
from legacy.dashboard.infrastructure.repositories.repository_factory import RepositoryFactory
from api.serialization import date_response

router = APIRouter(tags=["portfolio"])


@router.get("/portfolio/summary")
def get_portfolio_summary():
    """
    Full portfolio snapshot: KPIs, asset table, all chart series, available tags.
    Calls PortfolioController.get_data() and returns the presenter output directly.
    """
    data = PortfolioController().get_data()
    return date_response(data)


@router.get("/portfolio/history")
def get_portfolio_history(
    from_date: str = Query(None, alias="from"),
    to_date: str = Query(None, alias="to"),
):
    """
    Portfolio daily history series, optionally filtered by date range.
    Returns the same shape as portfolio_value_series / portfolio_pnl_series
    but as raw rows so the client can drive any chart.
    """
    rows_raw = RepositoryFactory.get("snapshot_query").get_unrealized_profit()
    rows = [dict(r._mapping) for r in rows_raw]

    if from_date:
        rows = [r for r in rows if str(r["data_date"]) >= from_date]
    if to_date:
        rows = [r for r in rows if str(r["data_date"]) <= to_date]

    return date_response(rows)
