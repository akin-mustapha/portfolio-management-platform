""" Tagging Service Module """
import logging
from src.services.portfolio.app.models import Asset, AssetTag, Tag
from src.services.portfolio.app.interfaces import BaseRepositoryInterface
from src.shared.utils.custom_logger import customer_logger

logging = customer_logger("tagging_service")

# What can it do
# Create a tag
# Create a asset
# Tag and asset
# Delete tagged from asset
# Get all asset by tag
# Get all tag by asset

class QueryRepositoryInterface:
  def select_asset_by_tag(self, tag_id: int):
    pass

  def select_tag_by_asset(self, asset_id: int):
    pass

  def select_all_tag_asset(self):
    pass


class PortfolioService:
  def __init__(self
               , asset_repository: BaseRepositoryInterface
               , tag_repository: BaseRepositoryInterface
               , asset_tag_repository: BaseRepositoryInterface
               , query_repository: QueryRepositoryInterface):
      """
      Docstring for __init__
      
        :param self: Description
        
        :return: Description


        USE CASE:
        - AS A USER, I should be able to create an asset
        - AS A USER, I WANT TO TAG ITEMS SO THAT I CAN ORGANIZE THEM BETTER.
        - AS A USER, I WANT TO ASSIGN MULTIPLE TAGS TO AN asset FOR BETTER CATEGORIZATION.
        - AS A USER, I WANT TO SEARCH FOR ASSETS BASED ON TAGS TO FIND RELATED CONTENT EASILY.
        - AS A USER, I WANT TO REMOVE TAGS FROM ASSETS WHEN THEY ARE NO LONGER RELEVANT.
        - AS A USER, I WANT TO VIEW ALL TAGS ASSOCIATED WITH AN ASSET TO UNDERSTAND ITS CATEGORIZATION.
        - AS A USER, I WANT TO MANAGE MY TAGS (CREATE, EDIT, DELETE) TO KEEP THEM ORGANIZED.
        - AS A USER I WANT TO BE ABLE TO ASSIGN CATEGORIES TO TAGS SO THAT I CAN BETTER ORGANIZE THEM.
      """
      logging.info("=" * 20)
      logging.info("Initializing TaggingService")
      logging.info("=" * 20)

      self._asset_repo = asset_repository
      self._tag_repo = tag_repository
      self._asset_tag_repo = asset_tag_repository
      self._query_repo = query_repository

  def create_asset(self, asset: Asset):
    """
    Create a new asset with an optional category.

    :param self: Description
    :param asset: The asset to create.
    :return: Description
    """
    try :
      logging.info(f"Creating asset: {asset.name}")
      asset = self._asset_repo.insert(asset)

      logging.info(f"Created asset with ID: {asset.id}")

      return asset
    except Exception as e:
        logging.error(f"Error creating asset: {e}")
        raise


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
    if not self._asset_repo.select(asset_tag.get("asset_id")):
        raise ValueError(f"Asset with ID {asset_tag.get("asset_id")} does not exist.")
    
    if not self._tag_repo.select(asset_tag.get("tag_id")):
        raise ValueError(f"Tag with ID {asset_tag.get("tag_id")} does not exist.")

    try:
      # logging.info(f"Tagging asset ID {asset_tag['asset_id']} with tag ID {asset_tag['tag_id']}")
      
      self._asset_tag_repo.insert_2(asset_tag)

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