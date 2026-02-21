# README

## Overview

Data model for tagging system

## Entities

- Asset
- Tag/Category
- Tag_type
- Asset_tag

## Rules

- An **Asset** can have more than one **Tag**
- A **Tag** can be assigned to more than one **Asset**
- An **Asset** can belong to an industry
- An **Asset** can belong to a sector
- An **Sector** can belong to an industry

## Action

- Akin invest in **S&P 500**, akin tags S&P 500 has ETF, AMERICA, CORE, DIVIDEND
<!-- - Akin creates new tag -->
<!-- - -->

## Model

### asset

---
Attribute

- id
- asset_external_id
- name
- description
- source_name
- is_active
- created_datetime
- updated_datetime

Behaviour

- deactivate_asset
- rename(new_name)
- update_description(new_description)
<!-- - add_tag -->

Constraint

- Unique(asset_external_id)
- PK(id)
<!-- - Unique asset_name -->

### asset_metric

---
Att

- id
- asset_id
- ma_30

### tag

---
Attribute

- id
- name
- description
- tag_type_id
- is_active
- created_datetime
- updated_datetime

Behaviour

- rename(new_name)
- update_description(new_description)
- deactivate_tag

Constraint

- Unique(name)
- PK(id)
- FK(tag_type_id) REF (tag_type.id)

### tag_type

---
Attribute

- id
- name
- is_active
- created_datetime
- updated_datetime

Behaviour

- rename(new_name)
- deactivate_tag_type

Constraint

- Primary key(id)

### asset_tag

---
Attribute

- id
- asset_id
- tag_id
- is_active
- created_datetime
- updated_datetime

Behaviour

- assign_tag_to_asset(asset_id, tag_id)
- deactivate

Constraint

- Unique(asset_id, tag_id)
- Foreign Key asset_id REFERENCE asset.id
- Foreign Key tag_id REFERENCE tag.id

---

## New Data

- industry
- sector
- market cap
- beta
- ETF (asset list)
