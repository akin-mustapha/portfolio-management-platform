"""
  Portfolio Service Module
"""
import logging
from src.services.portfolio.infra.repositories.repository_factory import RepositoryFactory

from src.services.portfolio.app.models import Asset, AssetTag, Tag, Category
from src.services.portfolio.app.models import Industry, Sector

from src.shared.utils.custom_logger import customer_logger

from datetime import datetime, UTC


logging = customer_logger("tagging_service")


class QueryRepositoryInterface:
  def select_asset_by_tag(self, tag_id: int):
    pass

  def select_tag_by_asset(self, asset_id: int):
    pass

  def select_all_tag_asset(self):
    pass


class PortfolioService:
  def __init__(self):
      """
      Docstring for __init__
      
        :param self: Description
        
        :return: Description
      """
      logging.info("=" * 20)
      logging.info("Initializing Tagging Service")
      logging.info("=" * 20)

      # self._asset_repo = asset_repository
      # self._tag_repo = tag_repository
      # self._asset_tag_repo = asset_tag_repository
      # self._query_repo = query_repository
      self._repo_factory = RepositoryFactory()

  # def create_asset(self, asset: Asset):
  #   """
  #   Create a new asset with an optional category.

  #   :param self: Description
  #   :param asset: The asset to create.
  #   :return: Description
  #   """
  #   try :
  #     logging.info(f"Creating asset: {asset.name}")
  #     asset = self._asset_repo.insert(asset)

  #     logging.info(f"Created asset with ID: {asset.id}")

  #     return asset
  #   except Exception as e:
  #       logging.error(f"Error creating asset: {e}")
  #       raise

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
      repo_sector.insert(data_dict)
      
    except Exception as e:
      logging.error(e)
      
      raise e
  
  def create_category(self, cateogry: Category):
    repo_category = self._repo_factory.get("category")

  def create_tag(self, tag: Tag):
    """
    Create a new tag with an optional category.

    :param self: Description
    :param tag: The tag to create.
    :return: Description
    """
    try:
      logging.info(f"Creating tag: {tag.name}")
      tag = self._tag_repo.insert(tag)

      logging.info(f"Created tag with ID: {tag.id}")
      return tag
    except Exception as e:
        logging.error(f"Error creating tag: {e}")
        raise
  
  # Controller while handle translating http parameters to domain models
  def tag_asset(self, asset_tag: dict):
    """
    Tag an asset with the provided tags.

    :param self: Description
    :param asset_id: The ID of the asset to tag.
    :param tags: A list of tags to assign to the asset.
    :return: Description
    """
    asset_repo = self._repo_factory.get("asset")
    tag_repo = self._repo_factory.get("tag")
    asset_tag_repo = self._repo_factory.get("asset_tag")
    
    if not asset_repo.select(asset_tag.get("asset_id")):
        raise ValueError(f"Asset with ID {asset_tag.get("asset_id")} does not exist.")
    
    if not tag_repo.select(asset_tag.get("tag_id")):
        raise ValueError(f"Tag with ID {asset_tag.get("tag_id")} does not exist.")

    try:
      # logging.info(f"Tagging asset ID {asset_tag['asset_id']} with tag ID {asset_tag['tag_id']}")
      
      asset_tag_repo.insert_2(asset_tag)

      # logging.info(f"Tagged asset ID {asset_tag['asset_id']} with tag ID {asset_tag['tag_id']}")
      return asset_tag
    except Exception as e:
        logging.error(f"Error tagging asset: {e}")
        raise

  def remove_tag_from_asset(self, item_tag: AssetTag):
    """
    Remove a specific tag from an asset.

    :param self: Description
    :param item_id: The ID of the asset to remove the tag from.
    :param tag: The tag to remove.
    :return: Description
    """
    try:
      self._asset_tag_repo.delete(item_tag)
    except Exception as e:
      logging.error(f"Error: {e}")
      raise

  def search_asset_by_tag(self, tag: Tag):
    """
    Search for items by a specific tag.

    :param self: Description
    :param tag: The tag to search for.
    :return: A list of items matching the given tag.
    """
    result = self._query_repo.select_asset_by_tag(tag.id)
    return result

  def search_tag_by_asset(self, asset: Asset):
    """
    Retrieve all tags associated with an asset.

    :param self: Description
    :param asset: The asset to retrieve tags for.
    :return: A list of tags associated with the given asset.
    """
    result = self._query_repo.select_tag_by_asset(asset.id)
    return result
  
  def get_all_tags(self):
     result = self._query_repo.select_all_tag_item()
     return result
   
   
if __name__ == "__main__":
  industry_1 = Industry(None, "Information Technology", "Information Technology", datetime.now(UTC), datetime.now(UTC))
  sector_1 = Sector(None, "4b2ff3e9-72f9-4be0-8b33-a72775da4a0b", "Semiconductors & Equipment", "Semiconductors & Equipment", datetime.now(UTC), datetime.now(UTC))
  
  portfolio_service = PortfolioService()
  portfolio_service.create_industry(industry_1)
  portfolio_service.create_sector(sector_1)