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
