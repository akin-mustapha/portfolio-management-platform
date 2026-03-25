---
name: refactoring
description: After multi-file refactors, verify imports resolve in both Prefect and dashboard contexts
---

After any multi-file refactor, run the test suite and verify all imports resolve. Prefect workers and the dashboard app may resolve imports differently (different working directories, different PYTHONPATH).

Do not remove variables that appear unused without first searching templates, callbacks, and conditional logic — especially theme variables like `ct` which are referenced dynamically.
