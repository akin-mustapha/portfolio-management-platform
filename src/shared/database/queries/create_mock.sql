
MERGE INTO portfolio.category AS tgt
USING (
  SELECT *
  FROM (
    VALUES('Portfolio')

  ) AS t1 (name)

) AS src (name)
  ON  tgt.name = src.name
WHEN NOT MATCHED
  THEN INSERT (name)
  VALUES(src.name)

;WITH cte AS (
  SELECT id FROM portfolio.category LIMIT 1
)
MERGE INTO portfolio.tag AS tgt
USING (
  SELECT *, cte.id
  FROM (
    VALUES  ('Core', 'Core Tag')
          , ('Satelite_europe', 'Core Tag')
          , ('Satelite_global', 'Core Tag')

  ) AS t1 (name, description)
  CROSS JOIN cte

) AS src (name, description, category_id)
  ON  tgt.name = src.name AND tgt.category_id = src.category_id

WHEN MATCHED AND tgt.description <> src.description THEN
  UPDATE
    SET description = src.description,
        updated_timestamp = NOW()
WHEN NOT MATCHED THEN
  INSERT (name, description, category_id)
  VALUES(src.name, src.description, src.category_id)



MERGE INTO portfolio.industry AS t1
USING (
  SELECT *
  FROM (
    VALUES('Consumer Cyclic', 'Consumer Cyclic')
  ) AS x1 (name, description)

) AS t2 (name, description)
ON t1.name = t2.name
WHEN MATCHED AND t1.description <> t2.description THEN
UPDATE
  SET name = t2.name
    , description = t2.description

WHEN NOT MATCHED THEN
  INSERT (name, description)
  VALUES(t2.name, t2.description)


;WITH cte AS (
  SELECT id FROM portfolio.industry LIMIT 1

)
MERGE INTO portfolio.sector AS t1
USING (
  SELECT *, cte.id
  FROM (
    VALUES('Consumer', 'Consumer 8')
  ) AS x1 (name, description)
  CROSS JOIN cte 
) AS t2 (name, description, industry_id)
ON t1.name = t2.name AND t1.industry_id = t2.industry_id
WHEN MATCHED AND t1.description <> t2.description THEN
UPDATE
  SET name = t2.name
    , description = t2.description
    , updated_timestamp = NOW()

WHEN NOT MATCHED THEN
  INSERT (name, description, industry_id)
  VALUES(t2.name, t2.description, t2.industry_id)


MERGE INTO portfolio.asset_tag AS t1
USING (

  SELECT a.id as asset_id, t.id as tag_id
  FROM portfolio.asset AS a
  CROSS JOIN portfolio.tag AS t
  LIMIT 30
) AS t2 (asset_id, tag_id)
ON t1.asset_id = t2.asset_id AND t1.tag_id = t2.tag_id
WHEN NOT MATCHED THEN
  INSERT (asset_id, tag_id)
  VALUES(t2.asset_id, t2.tag_id)
