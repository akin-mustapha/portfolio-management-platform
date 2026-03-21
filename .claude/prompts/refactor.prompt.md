Refactor the repository layer to use a consistent base class pattern. Spawn sub-agents for each task:

Agent 1: Audit all repository files and identify inconsistent patterns.
Agent 2: Implement the standardized base repository class.
Agent 3: Update all concrete repositories to extend the base class.
Agent 4: Run grep across the entire codebase to find and fix every broken import. After all agents complete, run the full test suite and fix any failures. Do not stop until pytest passes clean.


Before making any changes: 

1) Search for ALL imports of the modules we're about to move/rename, 
2) Check if Prefect flows and dashboard app use different import paths, 
3) List every file that will need import updates. Show me the full impact analysis before editing anything.