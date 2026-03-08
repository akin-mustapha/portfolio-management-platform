---
name: Asset-data-pipeline
description: Documentation on asset data ingestion pipeline
---

# Asset Data Pipeline

## Overview

Pipeline to ingest Trading 212 Asset API

## Processes

### Bronze Layer

- Full Loader Ingestion
- Partitioned Asset table, partitioned by date
- v_bronze_asset exposition abstraction view by current day partition

#### Bronze Tables

- `asset`
- `asset_YYYY_MM_DD`
- `v_bronze_asset` exposition abstraction view

#### Bronze Issues

- Error handling, api can return error due to rate limiting, especially when multiple pipelines are running

#### Bronze Solutions

- Error Handling
  - Implement Error handling logic in python
  - Write error to different table for inspection

### Silver Layer

- Incremental Loader
- asset table
- asset_computed table for computed columns

#### Silver Layer Tables

- `asset`
- `asset_computed`

#### Silver Issues

- Backfill, not possible from exposition abstraction
- Duplication from Bronze, batch run loads entire view

#### Silver Solutions

- Backfill - parameterize loader
- Implement Idempotency pattern, Update pattern,
  - define unique
  - implement merge logic, update when key match, insert when not

### Gold Layer

- Store data using star schema
