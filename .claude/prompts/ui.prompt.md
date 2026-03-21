Before editing, search all existing callbacks for any Output targeting the same chart component. Show me the search results before proceeding.

When modifying UI components (Dash callbacks, chart layouts), always verify there are no duplicate callback outputs across the entire app before adding new ones. Search for existing `Output('component-id', 'property')` patterns first.

Before making any dashboard changes, first create a validation script at tests/validate_callbacks.py that:

1) Imports all callback modules and checks for duplicate Output declarations across the entire app,
2) Verifies all referenced component IDs exist in layouts,
3) Checks that no imports reference non-existent modules.

Then implement the following UI changes: [DESCRIBE CHANGES HERE].

After each change, run the validation script AND start the Dash server to confirm no startup errors. If anything fails, fix it and re-validate. Do not consider the task complete until validation passes clean.
Copy