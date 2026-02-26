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
    
    # breakpoint()
    try:
      repo_sector.upsert(records=[data_dict], unique_key=["name"])
      
    except Exception as e:
      logging.error(e)
      
      raise e
  
  def create_category(self, cateogry: Category):
    repo_category = self._repo_factory.get("category")
    
    data_dict = cateogry.to_record()
    
    try:
      repo_category.upsert(records=[data_dict], unique_key=["name"])
      
    except Exception as e:
      logging.error(e)
      
      raise e
  

  def create_tag(self, tag: Tag):
    """
    Create a new tag with an optional category.

    :param self: Description
    :param tag: The tag to create.
    :return: Description
    """
    repo_tag = self._repo_factory.get("tag")
    data_dict = tag.to_record()
    
    try:
      logging.info(f"Creating tag: {tag.name}")
      res = repo_tag.upsert([data_dict], ["name", "tag_type_id"])
      logging.info(f"Created tag")
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
  industry_1 = Industry(
    id=None,
    name="Information Technology", 
    description="Information Technology", 
    created_timestamp=datetime.now(UTC))
  
  sector_1 = Sector(
    id=None,
    industry_id="4b2ff3e9-72f9-4be0-8b33-a72775da4a0b",
    name="Semiconductors & Equipment",
    description="Semiconductors & Equipment",
    created_timestamp=datetime.now(UTC))
  
  category_1 = Category(
    id=None,
    name="Country",
    description="Country Category",
    created_timestamp=datetime.now(UTC))
  tag_1 = Tag(None, "Semiconductors & Equipment", "Semiconductors & Equipment", "02dae516-dafb-4d12-a0c3-b066e6baa0b3", datetime.now(UTC))
  
  
  
  
  portfolio_service = PortfolioService()
  portfolio_service.create_industry(industry_1)
  portfolio_service.create_sector(sector_1)
  portfolio_service.create_category(category_1)
  portfolio_service.create_tag(tag_1)