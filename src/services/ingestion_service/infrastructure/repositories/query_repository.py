
class ItemSQLQueryRepository:
  def __init__(self, client):
    self.client = client

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
      res = client.excute(sql, params)

    return res