# Asset Data Pipeline

## Overview

Pipeline to ingest Trading 212 Asset API

## Processes

### Bronze Layer

- Full Loader Ingestion
- Partitioned Asset table, partitioned by date
- v_bronze_asset exposition abstraction view by current day partition

### Silver Layer

- Incremental Loader
- asset table
- asset_computed table for computed columns

#### Issues

- Backfill, not possible from exposition abstraction
- Duplication from Bronze, batch run loads entire view