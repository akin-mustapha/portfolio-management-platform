"""
Portfolio Service Module
"""

from backend.infrastructure.portfolio.repository_factory import RepositoryFactory
from backend.domain.portfolio.entities import (
    Asset,
    AssetTag,
    Tag,
    Category,
    Industry,
    Sector,
)

from shared.utils.custom_logger import customer_logger

logging = customer_logger("portfolio_service")


class PortfolioService:
    def __init__(self):
        logging.info("=" * 20)
        logging.info("Initializing Portfolio Service")
        logging.info("=" * 20)

        self._repo_factory = RepositoryFactory()

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
            raise ValueError(
                f"Asset with ID {asset_tag.get('asset_id')} does not exist."
            )

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
            asset_tag_repo.delete(
                {"asset_id": item_tag.asset_id, "tag_id": item_tag.tag_id}
            )
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
            sector_repo.update(
                params={"id": sector_id}, data={"industry_id": industry_id}
            )
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
