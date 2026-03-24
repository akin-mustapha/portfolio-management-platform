import pandas as pd
from ..infrastructure.repositories.repository_factory import RepositoryFactory
from ..presenters.portfolio_presenter import PortfolioPresenter


class PortfolioController:
    def __init__(self):
        self._presenter = PortfolioPresenter()
        self._query_factory = RepositoryFactory()

    def get_data(self):
        asset_data = self._query_factory.get(
            "asset_analytics"
        ).get_most_recent_asset_data()
        asset_data_history = self._query_factory.get(
            "asset_analytics"
        ).get_asset_history()
        portfolio_history = self._query_factory.get(
            "snapshot_query"
        ).get_unrealized_profit()

        df_asset_data = pd.DataFrame([dict(r._mapping) for r in asset_data])
        df_asset_data_history = pd.DataFrame(
            [dict(r._mapping) for r in asset_data_history]
        )
        df_portfolio_history = pd.DataFrame(
            [dict(r._mapping) for r in portfolio_history]
        )

        portfolio_snapshot = (
            df_portfolio_history.sort_values(by="data_date", ascending=False)
            .head(1)
            .to_dict("records")
        )

        tickers = df_asset_data["ticker"].tolist() if not df_asset_data.empty else []
        price_history = self._query_factory.get(
            "asset_analytics"
        ).get_portfolio_price_history(tickers)
        asset_tags_rows = self._query_factory.get("asset_analytics").get_asset_tags()

        price_map = {}
        for r in price_history:
            row = dict(r._mapping)
            price_map.setdefault(row["ticker"], []).append(float(row["price"]))

        tag_map = {}
        for r in asset_tags_rows:
            row = dict(r._mapping)
            tag_map.setdefault(row["ticker"].upper(), []).append(row["tag_name"])

        assets = df_asset_data.to_dict(orient="records")
        for row in assets:
            row["price_series"] = price_map.get(row["ticker"], [])
            row["tags"] = tag_map.get(row["ticker"].upper(), [])

        available_tags = sorted({tag for tags in tag_map.values() for tag in tags})
        data = {
            "assets": assets,
            "assets_history": df_asset_data_history,
            "portfolio_history": df_portfolio_history.to_dict(orient="records"),
            "portfolio_current_snapshot": (
                portfolio_snapshot[0] if portfolio_snapshot else {}
            ),
            "available_tags": available_tags,
        }
        return self._presenter.present(data)

    def get_ranked_bars(self, assets: list[dict], sort_by: str = "profit") -> tuple:
        winners = self._presenter._top_winner_bar_vm(assets, sort_by=sort_by)
        losers = self._presenter._top_losers_bar_vm(assets, sort_by=sort_by)
        return winners, losers
