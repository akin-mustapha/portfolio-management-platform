"""
Portfolio Service Module
"""

from shared.utils.custom_logger import customer_logger

from backend.application.portfolio.ports import (
    AssetAnalyticsPort,
    PortfolioQueryPort,
    RepositoryFactoryPort,
)
from backend.domain.portfolio.entities import (
    Asset,
    AssetTag,
    Category,
    Industry,
    Sector,
    Tag,
)
from backend.domain.portfolio.value_objects import TrendSignal

logging = customer_logger("portfolio_service")


class PortfolioService:
    def __init__(
        self,
        repo_factory: RepositoryFactoryPort,
        analytics_repo: AssetAnalyticsPort,
        portfolio_query_repo: PortfolioQueryPort,
    ):
        logging.info("=" * 20)
        logging.info("Initializing Portfolio Service")
        logging.info("=" * 20)

        self._repo_factory = repo_factory
        self._analytics_repo = analytics_repo
        self._portfolio_query_repo = portfolio_query_repo

    def create_industry(self, industry: Industry):
        repo_industry = self._repo_factory.get("industry")

        data_dict = industry.to_record()

        try:
            repo_industry.upsert(records=[data_dict], unique_key=["name"])

        except Exception as e:
            logging.error(e)

            raise e

    def create_sector(self, sector: Sector):
        repo_sector = self._repo_factory.get("sector")

        data_dict = sector.to_record()

        try:
            repo_sector.upsert(records=[data_dict], unique_key=["name"])

        except Exception as e:
            logging.error(e)

            raise e

    def create_category(self, category: Category):
        repo_category = self._repo_factory.get("category")

        data_dict = category.to_record()

        try:
            repo_category.upsert(records=[data_dict], unique_key=["name"])

        except Exception as e:
            logging.error(e)

            raise e

    def create_tag(self, tag: Tag):
        """
        Create a new tag with an optional category.

        :param tag: The tag to create.
        """
        repo_tag = self._repo_factory.get("tag")
        data_dict = tag.to_record()

        try:
            logging.info(f"Creating tag: {tag.name}")
            repo_tag.upsert([data_dict], ["name", "tag_type_id"])
            logging.info("Created tag")
            return tag
        except Exception as e:
            logging.error(f"Error creating tag: {e}")
            raise

    # Controller will handle translating http parameters to domain models
    def tag_asset(self, asset_tag: dict):
        """
        Tag an asset with the provided tags.

        :param asset_tag: Dict with asset_id and tag_id.
        """
        asset_repo = self._repo_factory.get("asset")
        tag_repo = self._repo_factory.get("tag")
        asset_tag_repo = self._repo_factory.get("asset_tag")

        if not asset_repo.select({"id": asset_tag.get("asset_id")}):
            raise ValueError(f"Asset with ID {asset_tag.get('asset_id')} does not exist.")

        if not tag_repo.select({"id": asset_tag.get("tag_id")}):
            raise ValueError(f"Tag with ID {asset_tag.get('tag_id')} does not exist.")

        try:
            asset_tag_repo.insert([asset_tag])
            return asset_tag
        except Exception as e:
            logging.error(f"Error tagging asset: {e}")
            raise

    def remove_tag_from_asset(self, item_tag: AssetTag):
        asset_tag_repo = self._repo_factory.get("asset_tag")

        try:
            asset_tag_repo.delete({"asset_id": item_tag.asset_id, "tag_id": item_tag.tag_id})
        except Exception as e:
            logging.error(f"Error removing tag from asset: {e}")
            raise

    def assign_industry_to_sector(self, sector_id: int, industry_id: int):
        sector_repo = self._repo_factory.get("sector")
        industry_repo = self._repo_factory.get("industry")

        if not industry_repo.select({"id": industry_id}):
            raise ValueError(f"Industry with ID {industry_id} does not exist.")

        if not sector_repo.select({"id": sector_id}):
            raise ValueError(f"Sector with ID {sector_id} does not exist.")

        try:
            sector_repo.update(params={"id": sector_id}, data={"industry_id": industry_id})
        except Exception as e:
            logging.error(f"Error assigning industry to sector: {e}")
            raise

    def search_asset_by_tag(self, tag: Tag):
        asset_tag_repo = self._repo_factory.get("asset_tag")

        if not tag.id:
            raise ValueError("Tag must have an id to search by.")

        try:
            return asset_tag_repo.select_all_by({"tag_id": tag.id})
        except Exception as e:
            logging.error(f"Error searching assets by tag: {e}")
            raise

    def search_tag_by_asset(self, asset: Asset):
        asset_tag_repo = self._repo_factory.get("asset_tag")

        if not asset.id:
            raise ValueError("Asset must have an id to search by.")

        try:
            return asset_tag_repo.select_all_by({"asset_id": asset.id})
        except Exception as e:
            logging.error(f"Error searching tags by asset: {e}")
            raise

    def search_tag_by_asset_id(self, asset_id: str):
        asset_tag_repo = self._repo_factory.get("asset_tag")

        if not asset_id:
            raise ValueError("asset_id is required to search tags.")

        try:
            return asset_tag_repo.select_all_by({"asset_id": asset_id})
        except Exception as e:
            logging.error(f"Error searching tags by asset_id: {e}")
            raise

    def get_all_tags(self):
        tag_repo = self._repo_factory.get("tag")
        result = tag_repo.select_all()
        return result

    def get_all_industries(self):
        industry_repo = self._repo_factory.get("industry")
        return industry_repo.select_all()

    def get_all_sectors(self):
        sector_repo = self._repo_factory.get("sector")
        return sector_repo.select_all()

    def get_all_categories(self):
        category_repo = self._repo_factory.get("category")
        return category_repo.select_all()

    def get_asset_by_name(self, name: str):
        asset_repo = self._repo_factory.get("asset")
        return asset_repo.select({"name": name})

    def get_asset_by_ticker(
        self,
        ticker: str,
        broker: str | None = None,
        currency: str | None = None,
    ):
        if not ticker:
            return None

        asset_repo = self._repo_factory.get("asset")
        params = {"ticker": ticker}
        if broker:
            params["broker"] = broker
        if currency:
            params["currency"] = currency
        return asset_repo.select(params)

    # -------------------------------------------------------------------------
    # Analytics read methods (gold layer)
    # -------------------------------------------------------------------------

    def get_asset_history(self, ticker: str, start: str, end: str) -> list[dict]:
        rows = self._analytics_repo.get_asset_snapshot(ticker, start, end)
        return [dict(r._mapping) for r in rows]

    def get_most_recent_assets(self, tag_filter: str | None = None) -> list[dict]:
        rows = [dict(r._mapping) for r in self._analytics_repo.get_most_recent_asset_data()]
        if tag_filter:
            tag_rows = [dict(r._mapping) for r in self._analytics_repo.get_asset_tags()]
            tag_map: dict[str, list[str]] = {}
            for r in tag_rows:
                tag_map.setdefault(r["ticker"].upper(), []).append(r["tag_name"])
            requested = {t.strip().lower() for t in tag_filter.split(",") if t.strip()}
            rows = [r for r in rows if requested & {t.lower() for t in tag_map.get(r["ticker"].upper(), [])}]
        return rows

    def get_portfolio_summary(self) -> dict:
        asset_rows = self.get_most_recent_assets()
        tickers = [r["ticker"] for r in asset_rows]

        price_history = self._analytics_repo.get_portfolio_price_history(tickers)
        price_map: dict[str, list[float]] = {}
        for r in price_history:
            row = dict(r._mapping)
            price_map.setdefault(row["ticker"], []).append(float(row["price"]))

        tag_rows = [dict(r._mapping) for r in self._analytics_repo.get_asset_tags()]
        tag_map: dict[str, list[str]] = {}
        for r in tag_rows:
            tag_map.setdefault(r["ticker"].upper(), []).append(r["tag_name"])

        for row in asset_rows:
            row["price_series"] = price_map.get(row["ticker"], [])
            row["tags"] = tag_map.get(row["ticker"].upper(), [])
            row["trend"] = str(TrendSignal.from_ma_crossover(row.get("value_ma_crossover_signal")))

        portfolio_history_rows = [dict(r._mapping) for r in self._portfolio_query_repo.get_unrealized_profit()]
        portfolio_snapshot = sorted(portfolio_history_rows, key=lambda r: r["data_date"], reverse=True)[:1]

        available_tags = sorted({tag for tags in tag_map.values() for tag in tags})

        assets_history = [dict(r._mapping) for r in self._analytics_repo.get_asset_history()]

        return {
            "assets": asset_rows,
            "assets_history": assets_history,
            "portfolio_history": portfolio_history_rows,
            "portfolio_current_snapshot": (portfolio_snapshot[0] if portfolio_snapshot else {}),
            "available_tags": available_tags,
        }

    def get_portfolio_history(self, from_date: str | None = None, to_date: str | None = None) -> list[dict]:
        rows = self._portfolio_query_repo.get_unrealized_profit(from_date, to_date)
        return [dict(r._mapping) for r in rows]

    def get_asset_profile(self, ticker: str) -> dict | None:
        rows = self.get_most_recent_assets()
        asset_row = next((r for r in rows if r["ticker"].upper() == ticker.upper()), None)
        if asset_row is None:
            return None
        tags = self.get_all_tags()
        industries = self.get_all_industries()
        sectors = self.get_all_sectors()
        categories = self.get_all_categories()
        current_tags = self._resolve_current_tags(
            asset_row.get("ticker", ""),
            tags,
            asset_row.get("broker"),
            asset_row.get("currency"),
        )
        return _present_asset_profile(asset_row, tags, industries, sectors, categories, current_tags)

    def _resolve_current_tags(
        self,
        ticker: str,
        all_tags: list,
        broker: str | None = None,
        currency: str | None = None,
    ) -> list:
        if not ticker:
            return []
        asset = self.get_asset_by_ticker(ticker, broker, currency)
        if not asset:
            return []
        tag_links = self.search_tag_by_asset_id(asset["id"])
        tag_id_to_name = {t["id"]: t["name"] for t in all_tags if t.get("id") and t.get("name")}
        return [tag_id_to_name[link["tag_id"]] for link in tag_links if link.get("tag_id") in tag_id_to_name]

    def assign_tag(self, ticker: str, tag_id: int) -> None:
        asset = self.get_asset_by_ticker(ticker)
        if not asset:
            raise KeyError(f"Asset '{ticker}' not found")
        self.tag_asset({"asset_id": asset["id"], "tag_id": tag_id})


def _present_asset_profile(
    asset_row: dict,
    tags: list,
    industries: list,
    sectors: list,
    categories: list,
    current_tags: list,
) -> dict:
    def _format_date(v) -> str:
        if v is None:
            return "—"
        s = str(v)
        return s[:10] if len(s) >= 10 else s

    def _to_options(items: list, label_key: str, value_key: str) -> list:
        return [
            {"label": i[label_key], "value": i[value_key]}
            for i in items
            if i.get(label_key) and i.get(value_key) is not None
        ]

    return {
        "ticker": asset_row.get("ticker", "—"),
        "name": asset_row.get("name", "—"),
        "description": asset_row.get("asset_description") or asset_row.get("name", "—"),
        "created": _format_date(asset_row.get("data_date")),
        "last_ingestion": _format_date(asset_row.get("data_date")),
        "tag_options": _to_options(tags, "name", "id"),
        "industry_options": _to_options(industries, "name", "id"),
        "sector_options": _to_options(sectors, "name", "id"),
        "category_options": _to_options(categories, "name", "id"),
        "current_tags": current_tags or [],
    }
