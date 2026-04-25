from dotenv import load_dotenv
from shared.database.client import SQLModelClient
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


# ===== Postgres Repos =====
class PostgresAssetQueryRepository:
    def __init__(self):
        self._client = SQLModelClient(database_url=DATABASE_URL)

    def get_most_recent_asset_data(self):
        sql = """
      WITH latest AS (
          SELECT asset_id, MAX(date_id) AS max_date_id
          FROM analytics.fact_valuation
          GROUP BY asset_id
      )
      SELECT
          da.ticker,
          da.name,
          da.name                                       AS asset_description,
          fv.value,
          fv.unrealized_pnl                             AS profit,
          fp.price,
          fp.avg_price,
          fv.cost_basis                                 AS cost,
          COALESCE(fv.position_weight_pct, 0)           AS weight_pct,
          COALESCE(fv.unrealized_pnl_pct, 0)            AS pnl_pct,
          ft.recent_profit_high_30d,
          ft.recent_profit_low_30d,
          ft.recent_value_high_30d,
          ft.recent_value_low_30d,
          ft.value_high_alltime,
          ft.value_low_alltime,
          ft.price_drawdown_pct_30d,
          ft.volatility_30d,
          ft.volatility_50d,
          ft.value_ma_30d,
          ft.value_ma_50d,
          fs.dca_bias,
          fr.cumulative_value_return,
          fr.daily_value_return,
          fs.value_ma_crossover_signal,
          ft.var_95_1d,
          ft.beta_60d,
          ft.sharpe_ratio_30d                           AS asset_sharpe_ratio_30d,
          COALESCE(fv.fx_impact, 0)                     AS fx_impact,
          TO_DATE(fv.date_id::TEXT, 'YYYYMMDD')         AS data_date
      FROM analytics.fact_valuation fv
      JOIN latest ON fv.asset_id = latest.asset_id AND fv.date_id = latest.max_date_id
      JOIN analytics.dim_asset da ON da.asset_id = fv.asset_id
      JOIN analytics.fact_price fp ON fp.asset_id = fv.asset_id AND fp.date_id = fv.date_id
      LEFT JOIN analytics.fact_technical ft ON ft.asset_id = fv.asset_id AND ft.date_id = fv.date_id
      LEFT JOIN analytics.fact_signal fs ON fs.asset_id = fv.asset_id AND fs.date_id = fv.date_id
      LEFT JOIN analytics.fact_return fr ON fr.asset_id = fv.asset_id AND fr.date_id = fv.date_id
    """
        with self._client as client:
            res = client.execute(sql)
            res = res.fetchall()
        return res

    def get_portfolio_price_history(self, tickers: list):
        if not tickers:
            return []
        placeholders = ", ".join(f":t{i}" for i in range(len(tickers)))
        params = {f"t{i}": t for i, t in enumerate(tickers)}
        sql = f"""
      SELECT
          da.ticker,
          fp.price,
          TO_DATE(fp.date_id::TEXT, 'YYYYMMDD')         AS data_date
      FROM analytics.fact_price fp
      JOIN analytics.dim_asset da ON da.asset_id = fp.asset_id
      WHERE fp.date_id >= TO_CHAR(CURRENT_DATE - INTERVAL '30 days', 'YYYYMMDD')::INTEGER
        AND da.ticker IN ({placeholders})
      ORDER BY da.ticker, fp.date_id ASC
    """
        with self._client as client:
            res = client.execute(sql, params)
        return res.fetchall()

    def get_asset_tags(self):
        sql = """
      SELECT da.ticker, t.name AS tag_name
      FROM analytics.dim_asset da
      JOIN portfolio.asset pa ON LOWER(da.ticker) = LOWER(pa.ticker)
      JOIN portfolio.asset_tag at ON pa.id = at.asset_id AND at.is_active = true
      JOIN portfolio.tag t ON at.tag_id = t.id AND t.is_active = true
    """
        with self._client as client:
            res = client.execute(sql)
        return res.fetchall()

    def get_asset_history(self):
        sql = """
      SELECT
          da.ticker,
          fv.unrealized_pnl                             AS profit,
          fv.value,
          fp.price,
          fv.cost_basis                                 AS cost,
          TO_DATE(fv.date_id::TEXT, 'YYYYMMDD')         AS data_date,
          CASE WHEN fv.unrealized_pnl > 0 THEN 1 ELSE 0 END AS is_profitable
      FROM analytics.fact_valuation fv
      JOIN analytics.dim_asset da ON da.asset_id = fv.asset_id
      JOIN analytics.fact_price fp ON fp.asset_id = fv.asset_id AND fp.date_id = fv.date_id
      WHERE fv.date_id >= TO_CHAR(CURRENT_DATE - INTERVAL '30 days', 'YYYYMMDD')::INTEGER
      ORDER BY da.ticker, fv.date_id ASC
    """
        with self._client as client:
            res = client.execute(sql)
        return res.fetchall()


class PostgresSnapshotQueryRepository:
    def __init__(self):
        self._client = SQLModelClient(database_url=DATABASE_URL)

    def select_asset_snapshot(self, params=None):
        sql = """
    SELECT a.name, at.*
    FROM portfolio.asset a
    INNER JOIN portfolio.asset_snapshot at ON a.id = at.asset_id
    """
        with self._client as client:
            res = client.execute(sql, params or {})
        return res.fetchall()

    def select_top_10_profit_asset_snapshot(self):
        sql = """
    SELECT a.name, a.description,
           avg(at.profit) as profit,
           avg(at.price) as price,
           avg(at.value) as value
    FROM portfolio.asset a
    INNER JOIN portfolio.asset_snapshot at ON a.id = at.asset_id
    GROUP BY a.id
    ORDER BY profit DESC
    LIMIT 10
    """
        with self._client as client:
            res = client.execute(sql)
        return res.fetchall()

    def get_unrealized_profit(self):
        sql = """
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
    WHERE dp.portfolio_id = '21641310'
    ORDER BY data_date ASC
    """
        with self._client as client:
            res = client.execute(sql)
        return res.fetchall()

    def get_asset_snapshot(self, ticker, start_date, end_date):
        sql = """
        SELECT
            da.ticker,
            da.name                                       AS asset_description,
            ft.recent_value_high_30d,
            ft.recent_value_low_30d,
            ft.price_ma_20d,
            ft.price_ma_50d,
            fs.dca_bias,
            fv.value,
            fp.avg_price,
            fp.price,
            fv.unrealized_pnl                             AS profit,
            COALESCE(fv.fx_impact, 0)                     AS fx_impact,
            ft.volatility_30d,
            ft.price_drawdown_pct_30d,
            fr.cumulative_value_return,
            fr.daily_value_return,
            TO_DATE(fv.date_id::TEXT, 'YYYYMMDD')         AS data_date
        FROM analytics.fact_valuation fv
        JOIN analytics.dim_asset da ON da.asset_id = fv.asset_id
        JOIN analytics.fact_price fp ON fp.asset_id = fv.asset_id AND fp.date_id = fv.date_id
        LEFT JOIN analytics.fact_technical ft ON ft.asset_id = fv.asset_id AND ft.date_id = fv.date_id
        LEFT JOIN analytics.fact_signal fs ON fs.asset_id = fv.asset_id AND fs.date_id = fv.date_id
        LEFT JOIN analytics.fact_return fr ON fr.asset_id = fv.asset_id AND fr.date_id = fv.date_id
        WHERE TO_DATE(fv.date_id::TEXT, 'YYYYMMDD') BETWEEN :start_date AND :end_date
          AND LOWER(da.ticker) = :ticker
        ORDER BY fv.date_id ASC
      """
        with self._client as client:
            res = client.execute(
                sql,
                {
                    "ticker": ticker.lower(),
                    "start_date": start_date,
                    "end_date": end_date,
                },
            )
        return res.fetchall()


# ===== SQLite Repos =====
class SQLiteAssetQueryRepository(PostgresAssetQueryRepository):
    def get_portfolio_price_history(self, tickers: list):
        if not tickers:
            return []
        placeholders = ", ".join(f":t{i}" for i in range(len(tickers)))
        params = {f"t{i}": t for i, t in enumerate(tickers)}
        sql = f"""
      SELECT ticker, price, created_timestamp as data_date
      FROM asset
      WHERE created_timestamp >= datetime('now', '-30 days')
        AND ticker IN ({placeholders})
      ORDER BY ticker, created_timestamp ASC
    """
        with self._client as client:
            res = client.execute(sql, params)
        return res.fetchall()


class SQLiteSnapshotQueryRepository(PostgresSnapshotQueryRepository):
    def select_top_10_profit_asset_snapshot(self):
        sql = """
    SELECT a.name, a.description,
           avg(at.profit) as profit,
           avg(at.price) as price,
           avg(at.value) as value
    FROM asset a
    INNER JOIN asset_snapshot at ON a.id = at.asset_id
    GROUP BY a.id
    ORDER BY profit DESC
    LIMIT 10
    """
        with self._client as client:
            res = client.execute(sql)
        return res.fetchall()
