# Meta Cycles for Aider

This folder contains a meta-cycle system to automate your coding processes with Aider.

## How It Works
1. **`meta_cycle_manager.aiderscript`** loads `meta_cycle.json`, checks which cycle is incomplete, and instructs Aider to `/load` the correct `.aiderscript`.
2. **`fix_bug_cycle.aiderscript`, `feature_dev_cycle.aiderscript`, etc.** contain the actual commands to fix bugs or develop features.
3. Update `meta_cycle.json` to mark cycles "completed" when youre done.

## Steps to Use
1. From the Aider prompt, run `/load meta_cycle_manager.aiderscript`.
2. Aider will execute the Python code in that file, which prints `/load fix_bug_cycle.aiderscript` (or whichever is next).
3. Aider then automatically loads the child script to do your coding steps.

That's it, sir. Enjoy!
