"""
  Portfolio Service Module
"""
from .infrastructure.repositories.repository_factory import RepositoryFactory
from .domain.entities import Asset, AssetTag, Tag, Category, Industry, Sector
from .app.interfaces import AssetQueryRepository

from shared.utils.custom_logger import customer_logger

from datetime import datetime, UTC


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
      logging.info(f"Created tag")
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

    if not asset_repo.select(asset_tag.get("asset_id")):
      raise ValueError(f"Asset with ID {asset_tag.get('asset_id')} does not exist.")

    if not tag_repo.select(asset_tag.get("tag_id")):
      raise ValueError(f"Tag with ID {asset_tag.get('tag_id')} does not exist.")

    try:
      asset_tag_repo.insert([asset_tag])
      return asset_tag
    except Exception as e:
      logging.error(f"Error tagging asset: {e}")
      raise

  def remove_tag_from_asset(self, item_tag: AssetTag):
    raise NotImplementedError("remove_tag_from_asset: not yet implemented")

  def search_asset_by_tag(self, tag: Tag):
    raise NotImplementedError("search_asset_by_tag: not yet implemented")

  def search_tag_by_asset(self, asset: Asset):
    raise NotImplementedError("search_tag_by_asset: not yet implemented")

  def get_all_tags(self):
    tag_repo = self._repo_factory.get("tag")
    result = tag_repo.select_all()
    return result
