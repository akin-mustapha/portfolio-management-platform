---
name: database
description: Use this skill when answering queries, working, developing on the database
---

**DO NOT READ CODE**

# Why

This provides the needed context to understand the current database infrastructure and implemenation of this codebase. You should keep answer focused the database.

# How

# Data Storage Model

The data storage used is postgres sql database which runs on a docker container.

The database is setup like as a medallion layer (Bronze, Silver, Gold). Each layer is current separated by the database schema (Bronze -> Raw, Silver -> Staging, Gold -> Analytics)

**Bronze**
This layer stores raw unprocessed data. Right now data are stored in `raw.asset` and `raw.account`, each then partitioned by ingestion date, later then exposed using an exposition view `v_bronze_account` and `v_bronze_asset`

**Silver**
This layer holds transformed and computed data from the raw bronze database.

**Gold**
This layer uses a kimball data model to present the usecase data


## Migration
Database deployments are handles by alembic

## Schema Reference
./references/schema-reference.md