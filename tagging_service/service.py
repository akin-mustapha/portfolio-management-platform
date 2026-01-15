""" Tagging Service Module """
import logging
from random import randint
from datetime import UTC, datetime

from database.client import SQLModelClient
from repository.base_repository import BaseRepository
from repository.entity_repository import EntityRepository
from repository.query_repository import ItemSQLQueryRepository
from tagging_service.models.models import Item, Item_tag, Tag
from tagging_service.repositories import DomainRepositoryFactory




# TODO: Log to file_name, keep services logs separate
logging.basicConfig(level=logging.INFO, filename='logs/info.log', filemode='a', format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')

# What can it do
# Create a tag
# Create a item
# Tag and item
# Delete tagged from item
# Get all item by tag
# Get all tag by item

class TaggingService:
  def __init__(self
               , item_repository: BaseRepository
               , tag_repository: BaseRepository
               , item_tag_repository: BaseRepository
               , query_repository):
      """
      Docstring for __init__
      
        :param self: Description
        
        :return: Description


        USE CASE:
        - AS A USER, I should be able to create an item
        - AS A USER, I WANT TO TAG ITEMS SO THAT I CAN ORGANIZE THEM BETTER.
        - AS A USER, I WANT TO ASSIGN MULTIPLE TAGS TO AN ITEM FOR BETTER CATEGORIZATION.
        - AS A USER, I WANT TO SEARCH FOR ITEMS BASED ON TAGS TO FIND RELATED CONTENT EASILY.
        - AS A USER, I WANT TO REMOVE TAGS FROM ITEMS WHEN THEY ARE NO LONGER RELEVANT.
        - AS A USER, I WANT TO VIEW ALL TAGS ASSOCIATED WITH AN ITEM TO UNDERSTAND ITS CATEGORIZATION.
        - AS A USER, I WANT TO MANAGE MY TAGS (CREATE, EDIT, DELETE) TO KEEP THEM ORGANIZED.
        - AS A USER I WANT TO BE ABLE TO ASSIGN CATEGORIES TO TAGS SO THAT I CAN BETTER ORGANIZE THEM.
      """
      logging.info("=" * 20)
      logging.info("Initializing TaggingService")
      logging.info("=" * 20)

      self.item_repo = item_repository
      self.tag_repo = tag_repository
      self.item_tag_repo = item_tag_repository
      self.query_repo = query_repository

  def create_item(self, item: Item):
    """
    Create a new item with an optional category.

    :param self: Description
    :param item: The item to create.
    :return: Description
    """
    try :
      logging.info(f"Creating item: {item.name}")
      item = self.item_repo.insert(item)

      logging.info(f"Created item with ID: {item.id}")

      return item
    except Exception as e:
        logging.error(f"Error creating item: {e}")
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
      tag = self.tag_repo.insert(tag)

      logging.info(f"Created tag with ID: {tag.id}")
      return tag
    except Exception as e:
        logging.error(f"Error creating tag: {e}")
        raise
  
  # Controller while handle translating http parameters to domain models
  def tag_item(self, item_tag: Item_tag):
    """
    Tag an item with the provided tags.

    :param self: Description
    :param item_id: The ID of the item to tag.
    :param tags: A list of tags to assign to the item.
    :return: Description
    """
    if not self.item_repo.select(item_tag.item_id):
        raise ValueError(f"Item with ID {item_tag.item_id} does not exist.")
    
    if not self.tag_repo.select(item_tag.tag_id):
        raise ValueError(f"Tag with ID {item_tag.tag_id} does not exist.")

    try:
      logging.info(f"Tagging item ID {item_tag.item_id} with tag ID {item_tag.tag_id}")
      
      self.item_tag_repo.insert(item_tag)

      logging.info(f"Tagged item ID {item_tag.item_id} with tag ID {item_tag.tag_id}")
      return item_tag
    except Exception as e:
        logging.error(f"Error tagging item: {e}")
        raise

  def remove_tag_from_item(self, item_tag: Item_tag):
    """
    Remove a specific tag from an item.

    :param self: Description
    :param item_id: The ID of the item to remove the tag from.
    :param tag: The tag to remove.
    :return: Description
    """
    try:
      self.item_tag_repo.delete(item_tag)
    except Exception as e:
      logging.error(f"Error: {e}")
      raise

  def search_item_by_tag(self, tag: Tag):
    """
    Search for items by a specific tag.

    :param self: Description
    :param tag: The tag to search for.
    :return: A list of items matching the given tag.
    """
    result = self.query_repo.select_item_by_tag(tag.id)

    return result

  def search_tag_by_item(self, item: Item):
    """
    Retrieve all tags associated with an item.

    :param self: Description
    :param item_id: The ID of the item to retrieve tags for.
    :return: A list of tags associated with the given item.
    """
    result = self.query_repo.select_tag_by_item(item.id)

    return result


if __name__ == "__main__":
  # Example usage
  t_item = Item(
              id=4,
              external_id=f"instrument_{randint(1000, 9999)}",
              name="Sample Instrument",
              description="Sample Instrument Description",
              source_name="trading212",
              is_active=True,
              created_datetime=datetime.now(UTC),
              updated_datetime=None,
          )

  t_tag = Tag(
              id=1,
              name=f"Sample Tag_{randint(1000, 9999)}",
              description="Sample Tag Description",
              tag_type_id=randint(1, 5),
              is_active=True,
              created_datetime=datetime.now(UTC),
              updated_datetime=None,
          )

  database_client = SQLModelClient(database_url="sqlite:///./data/trading212.db")

  item_repo = DomainRepositoryFactory.get_repository("item", EntityRepository("asset", client=database_client))

  tag_repo = DomainRepositoryFactory.get_repository("tag", EntityRepository("tag", client=database_client))

  item_tag_repo = DomainRepositoryFactory.get_repository("item_tag", EntityRepository("asset_tag", client=database_client))

  item_query_repo = ItemSQLQueryRepository(database_client)


  tag_service = TaggingService(item_repo, tag_repo, item_tag_repo, item_query_repo)

  # res = tag_service.create_item(t_item)
  # print(res)

  # res_tag = tag_service.create_tag(t_tag)
  # print(res_tag)

  t_tag_item = Item_tag(
                item_id=4,
                tag_id=1,
                is_active=True,
                created_datetime=datetime.now(UTC),
                updated_datetime=None,
            )
  # res_tag_item = tag_service.tag_item(t_tag_item)
  # print(res_tag_item)

  # tag_service.remove_tag_from_item(t_tag_item)
  # tag_service.tag_item(t_tag_item)


  x = tag_service.search_item_by_tag(t_tag)
  y = tag_service.search_tag_by_item(t_item)

  print(x)
  print(y)
