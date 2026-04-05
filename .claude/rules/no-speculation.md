---
name: no-speculation
description: Don't add fields, tables, or features not tied to a specific requirement
---

Don't add fields, tables, or features not tied to a specific requirement or dashboard question. Don't design for hypothetical future requirements.

This applies specifically to:
- Gold layer tables and columns — only add what a dashboard question explicitly requires
- Pydantic schema fields
- Database columns or indexes
- Abstraction layers or helper utilities
