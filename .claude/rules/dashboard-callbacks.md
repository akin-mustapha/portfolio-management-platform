---
name: dashboard-callbacks
description: Check for duplicate callback outputs before adding new ones; confirm layout direction with user
---

Before adding any callback output, search for existing `Output('component-id', 'property')` patterns across all callback files to avoid duplicate output registrations — Dash will raise a hard error at startup.

For layout direction (horizontal vs vertical), confirm with the user before implementing. Default to side-by-side for chart pairs.

Do not remove variables that appear unused without first searching templates, callbacks, and conditional logic — especially theme variables like `ct`.
