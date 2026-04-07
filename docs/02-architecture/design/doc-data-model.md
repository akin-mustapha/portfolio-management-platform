# README

## Overview

Data model for tagging system

## Entities

- Asset
- Tag
- Category
- AssetTag
- Industry
- Sector

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
- external_id
- name
- description
- source_name
- is_active
- created_timestamp

Behaviour

- deactivate_asset
- rename(new_name)
- update_description(new_description)
<!-- - add_tag -->

Constraint

- Unique(external_id)
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
- tag_type_id  ← domain entity name; mapped to DB column `category_id` by the repository layer
- is_active
- created_timestamp
- updated_timestamp

Behaviour

- rename(new_name)
- update_description(new_description)
- deactivate_tag

Constraint

- Unique(name)
- PK(id)
- FK(category_id) REF (category.id)  ← DB column name; domain uses `tag_type_id`

### category

---
Attribute

- id
- name
- is_active
- created_timestamp
- updated_timestamp

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
- created_timestamp
- updated_timestamp

Behaviour

- assign_tag_to_asset(asset_id, tag_id)
- deactivate

Constraint

- Unique(asset_id, tag_id)
- Foreign Key asset_id REFERENCE asset.id
- Foreign Key tag_id REFERENCE tag.id

---

### industry

---
Attribute

- id
- name
- description
- created_timestamp

Constraint

- PK(id)
- Unique(name)

Domain rule: name is required and must be unique

### sector

---
Attribute

- id
- industry_id
- name
- description
- created_timestamp

Constraint

- PK(id)
- Unique(name)
- FK(industry_id) REF (industry.id)

Domain rule: industry_id is required; a sector must belong to an industry

---

## New Data

- market cap
- beta
- ETF (asset list)
