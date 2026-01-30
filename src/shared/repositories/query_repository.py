
class ItemSQLQueryRepository:
  def __init__(self, client):
    self.client = client

  def select_all_asset(self):
    sql = f"""
      SELECT
        a.id as asset_id
      ,	a.name as asset_name
      FROM asset a
      WHERE a.is_active = 1
    """
    with self.client as client:
      res = client.execute(sql)
    return res.fetchall()
  
  def select_all_tag(self):
    sql = f"""
      SELECT
        t.id as tag_id
      ,	t.name as tag_name
      FROM tag t
      WHERE t.is_active = 1
    """
    with self.client as client:
      res = client.execute(sql)
    return res.fetchall()
    
  def select_all_tag_item(self):
    sql = f"""
      SELECT
        at.asset_id
      ,	a.name as asset_name
      , at.tag_id 
      ,	t.name as tag_name
      FROM asset a 
        INNER JOIN asset_tag at
          ON a.id = at.asset_id
        INNER JOIN tag t
          ON at.tag_id = t.id
    """
    with self.client as client:
      res = client.execute(sql)
    return res.fetchall()
  
  def select_item_by_tag(self, tag_id):
    sql = f"""
      SELECT
        at.asset_id t_id
      ,	a.name as asset_name
      , at.tag_id 
      ,	t.name as asset_name
      FROM asset a 
        INNER JOIN asset_tag at
          ON a.id = at.asset_id
        INNER JOIN tag t
          ON at.tag_id = t.id
      WHERE t.id = :tag_id
    """
    params = {'tag_id': tag_id}
    with self.client as client:
      res = client.execute(sql, params)
    return res.fetchall()
  
  def select_tag_by_item(self, item_id):
    sql = f"""
      SELECT
        at.asset_id t_id
      ,	a.name as asset_name
      , at.tag_id 
      ,	t.name as asset_name
      FROM asset a 
        INNER JOIN asset_tag at
          ON a.id = at.asset_id
        INNER JOIN tag t
          ON at.tag_id = t.id
      WHERE a.id = :item_id
    """
    params = {'item_id': item_id}

    with self.client as client:
      res = client.execute(sql, params)
    return res.fetchall()

  def select_item_by_parameter(self, params):
    filter = [f'{k} = :{k}' for k in params.keys()]
    filter_str = ' AND'.join(filter)
    sql = f"""
      SELECT
        at.asset_id t_id
      ,	a.name as asset_name
      , at.tag_id 
      ,	a.name as asset_name
      FROM asset a 
        INNER JOIN asset_tag at
          ON a.id = at.asset_id
        INNER JOIN tag t
          ON at.tag_id = t.id
      WHERE {filter_str}
    """

    with self.client as client:
      res = client.execute(sql, params)

    return res
  

class SnapshotSQLQueryRepository:
  def __init__(self, client):
    self.client = client
  def select_asset_snapshot(self, params=None):
    sql = f"""
      SELECT
        a.name,
        at.*
      FROM asset a 
        INNER JOIN asset_snapshot at
          ON a.id = at.asset_id
    """
    with self.client as client:
      res = client.execute(sql, params)
    return res.fetchall()
  
  def select_top_10_profit_asset_snapshot(self, params=None):
    sql = f"""
      SELECT
        a.name as name,
        a.description as description,
        avg(at.profit) as profit,
        avg(at.price) as price,
        avg(at.value) as value
      FROM asset a 
        INNER JOIN asset_snapshot at
          ON a.id = at.asset_id
      GROUP BY asset_id
      ORDER BY profit DESC
    """
    with self.client as client:
      res = client.execute(sql, params)
    return res.fetchall()
  
  def select_portfolio_unrealized_return(self):
    sql = """
      SELECT
        data_date,
        current_value AS portfolio_value,
        unrealized_profit AS unrealized_return
      FROM portfolio_snapshot
      WHERE external_id iS NOT NULL
      GROUP BY data_date
      ORDER BY data_date
    """
    with self.client as client:
        res = client.execute(sql)
    return res.fetchall()