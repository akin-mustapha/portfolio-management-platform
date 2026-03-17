import os
from dotenv import load_dotenv
from shared.database.client import SQLModelClient
import logging

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

logging.basicConfig(
    level=logging.INFO,
    filename='logs/info.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s'
)


def sychronize_industry():
  target = 'staging.industry'
  source = 'portfolio.industry'
  sql = f'''
    UPDATE {target}
    SET to_timestamp = CURRENT_DATE
      , is_current = false
    FROM {target} as tgt
      INNER JOIN {source} src
        ON tgt.industry_id = src.id
    WHERE tgt.is_current = true
      AND (
          tgt.name <> src.name
        OR 
          tgt.description <> src.description
      );

  INSERT INTO {target} (industry_id, name, description)
  SELECT src.id, src.name, src.description
  FROM {target} tgt
    RIGHT JOIN {source} src
      ON tgt.industry_id = src.id
        AND tgt.is_current = true
  WHERE tgt.industry_id IS NULL;
  '''
  
  with SQLModelClient(database_url=DATABASE_URL) as client:
    client.execute(sql)
    
    
def sychronize_sector():
  target = 'staging.sector'
  source = 'portfolio.sector'
  sql = f'''
    UPDATE {target}
    SET to_timestamp = CURRENT_DATE
      , is_current = false
    FROM {target} as tgt
      INNER JOIN {source} src
        ON tgt.sector_id = src.id
    WHERE tgt.is_current = true
      AND (
          tgt.name <> src.name
        OR 
          tgt.industry_id <> src.industry_id
        OR 
          tgt.description <> src.description
      );

  INSERT INTO {target} (sector_id, industry_id, name, description)
  SELECT src.id, src.industry_id, src.name, src.description
  FROM {target} tgt
    RIGHT JOIN {source} src
      ON tgt.sector_id = src.id
        AND tgt.is_current = true
  WHERE tgt.sector_id IS NULL;
  '''
  
  with SQLModelClient(database_url=DATABASE_URL) as client:
    client.execute(sql)
    
    
def sychronize_tag():
  target = 'staging.tag'
  source = 'portfolio.tag'
  sql = f'''
    UPDATE {target}
    SET to_timestamp = CURRENT_DATE
      , is_current = false
    FROM {target} as tgt
      INNER JOIN {source} src
        ON tgt.tag_id = src.id
    WHERE tgt.is_current = true
      AND (
          tgt.name <> src.name
        OR 
          tgt.category_id <> src.category_id
        OR 
          tgt.description <> src.description
      );

  INSERT INTO {target} (tag_id, name, description, category_id)
  SELECT src.id, src.name, src.description, src.category_id
  FROM {target} tgt
    RIGHT JOIN {source} src
      ON tgt.tag_id = src.id
        AND tgt.is_current = true
  WHERE tgt.tag_id IS NULL;
  '''
  
  with SQLModelClient(database_url=DATABASE_URL) as client:
    client.execute(sql)
    
    
    
def sychronize_category():
  target = 'staging.category'
  source = 'portfolio.category'
  sql = f'''
    UPDATE {target}
    SET to_timestamp = CURRENT_DATE
      , is_current = false
    FROM {target} as tgt
      INNER JOIN {source} src
        ON tgt.category_id = src.id
    WHERE tgt.is_current = true
      AND (
          tgt.name <> src.name
        OR 
          tgt.description <> src.description
      );

  INSERT INTO {target} (category_id, name, description)
  SELECT src.id, src.name, src.description
  FROM {target} tgt
    RIGHT JOIN {source} src
      ON tgt.category_id = src.id
        AND tgt.is_current = true
  WHERE tgt.category_id IS NULL;
  '''
  
  with SQLModelClient(database_url=DATABASE_URL) as client:
    client.execute(sql)
    
    
def sychronize_asset_tag():
  target = 'staging.asset_tag'
  source = 'portfolio.asset_tag'
  sql = f'''
    UPDATE {target}
    SET to_timestamp = CURRENT_DATE
      , is_current = false
    FROM {target} as tgt
        LEFT JOIN {source} src
        ON tgt.asset_id = src.asset_id
        AND tgt.tag_id = src.tag_id
    WHERE tgt.is_current = true
      AND tgt.id IS NULL;

  INSERT INTO {target} (asset_id, tag_id)
  SELECT src.asset_id, src.tag_id
  FROM {target} tgt
    RIGHT JOIN {source} src
        ON tgt.asset_id = src.asset_id
        AND tgt.tag_id = src.tag_id
        AND tgt.is_current = true
  WHERE tgt.tag_id IS NULL AND tgt.asset_id IS NULL;
  '''
  
  with SQLModelClient(database_url=DATABASE_URL) as client:
    client.execute(sql)


def enrichment_sychronization():
  logging.info('Sychronizing Industry')
  sychronize_industry()
  
  logging.info('Sychronizing Sector')
  
  sychronize_sector()
  
  logging.info('Sychronizing Tag')
  sychronize_tag()
  
  logging.info('Sychronizing Category')
  sychronize_category()
  
  logging.info('Sychronizing Asset Tag')
  sychronize_asset_tag()
