import os

from dotenv import load_dotenv
from shared.database.client import SQLModelClient

load_dotenv()

_DATABASE_URL = os.getenv("DATABASE_URL")


class PortfolioQueryRepository:
    def __init__(self):
        self._client = SQLModelClient(database_url=_DATABASE_URL)

    def get_unrealized_profit(
        self,
        from_date: str | None = None,
        to_date: str | None = None,
    ):
        date_filter = ""
        params: dict = {}
        if from_date:
            date_filter += " AND TO_DATE(fpd.date_id::TEXT, 'YYYYMMDD') >= :from_date"
            params["from_date"] = from_date
        if to_date:
            date_filter += " AND TO_DATE(fpd.date_id::TEXT, 'YYYYMMDD') <= :to_date"
            params["to_date"] = to_date

        sql = f"""
        SELECT
            TO_DATE(fpd.date_id::TEXT, 'YYYYMMDD')        AS data_date,
            fpd.total_value,
            fpd.total_cost                                AS investments_total_cost,
            fpd.realized_pnl                              AS investments_realized_pnl,
            fpd.unrealized_pnl                            AS investments_unrealized_pnl,
            dp.base_currency                              AS currency,
            fpd.cash_available                            AS cash_available_to_trade,
            COALESCE(fpd.cash_reserved, 0)               AS cash_reserved_for_orders,
            COALESCE(fpd.cash_in_pies, 0)                AS cash_in_pies,
            COALESCE(fpd.portfolio_volatility_weighted, 0) AS portfolio_volatility_weighted,
            COALESCE(fpd.daily_value_change_pct, 0)        AS daily_value_change_pct,
            COALESCE(fpd.daily_value_change_abs, 0)        AS daily_value_change_abs,
            COALESCE(fpd.fx_impact_total, 0)              AS fx_impact_total,
            fpd.portfolio_beta_weighted,
            fpd.sharpe_ratio_30d,
            fpd.benchmark_return_daily,
            fpd.portfolio_vs_benchmark_30d
        FROM analytics.fact_portfolio_daily fpd
        JOIN analytics.dim_portfolio dp ON dp.id = fpd.portfolio_id
        WHERE dp.portfolio_id = '21641310'{date_filter}
        ORDER BY data_date ASC
        """
        return self._client.execute(sql, params)
