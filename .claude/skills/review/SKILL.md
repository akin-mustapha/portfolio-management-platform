---
name: review
description: Use this SKILL when doing code review
---

## Code Review Checklist
1. Search for duplicate Dash callback outputs before adding new ones
2. Verify no references to unapplied migration columns
3. Check all imports resolve in both Prefect and dashboard contexts
4. Don't flag theme variables (ct, etc.) as dead code
5. Run: python -m pytest tests/ --tb=short
