
## Meta Cycles System Architecture


## Managing Cycles
- **Cycle Transition**: Each cycle determines and sets the next appropriate cycle
- **Cycle Completion**: Cycles should always end by loading the next cycle
- **Project Completion**: Use stop_cycle when reaching a milestone or project end

## Cycle Transition Verification Checklist
1. Each cycle must:
   - Have exactly one /load directive pointing to the next cycle
   - Maintain clear transition documentation
   - Handle error conditions gracefully
   - Record metrics before transition
   - Validate dependencies before transition
   - Clean up resources before transition

## Best Practices
1. Keep chooser.aiderscript clean:
   - Only update the /load directive
   - Never add logic or code
2. Maintain cycle independence:
   - Each cycle should be self-contained
   - Use dependency management for cross-cycle requirements
3. Use stop_cycle for:
   - Project milestones
   - Final project completion
   - System maintenance breaks


Below is a **concise guide** to **Aider scripting** for your LLM, emphasizing how to create and run external code files, and the usage of `/ask`, `/code`, and `/load`:

---

## 1. No Code in `.aiderscript` Directly
- You **cannot** embed Python (or any code) in `.aiderscript` files themselves.
- Instead, **create external scripts** in a `scripts/` folder (e.g. `scripts/my_code.py`).

---

## 2. Creating and Editing Files
- **Use `/ask`** for questions or high-level requests (LLM provides suggestions, no file edits).
  - E.g. `/ask How to handle user input in Python?`
- **Use `/code`** for instructions that **edit** existing files or create new ones (in context).
  - E.g. `/code Create scripts/my_code.py with a function parse_input() that prints user data.`

---

## 3. Running Code
- To run external scripts created in `scripts/`, use:
  ```
  /run scripts/my_code.py
  ```
- This executes the file in your local environment (similar to shell commands).

---

## 4. Loading Another `.aiderscript`
- Use:
  ```
  /load some_other_file.aiderscript
  ```
- This transfers control to the next script, continuing your workflow.

---

## 5. Single-Line Prompts
- **Important**: Each `/ask`, `/code`, `/run`, `/load` command must be on **one line**.  
- Example (correct):
  ```
  /ask How do we handle negative values in parse_input?
  ```
  (Incorrect would be line breaks in the prompt.)

---

## Summary
1. **Create/modify external code** by `/code` instructions or `/ask` Q&A, but **no code** inside `.aiderscript`.
2. **Run** created scripts using `/run scripts/...`.
3. **Load** the next `.aiderscript` with `/load`.
4. Keep each command prompt on **one line**.

Following these rules ensures a **clean**, **modular** Aider scripting workflow.

# Cycle Transition Rules:
# 1. Each cycle determines and sets the next appropriate cycle
# 2. Only update the /load directive to point to the next cycle. IMPORTANT! There can only be one /load directive at end of a code cycle file! If you have two, the second one will never execute.
# 3. Never add logic or code to this file
# 4. Use stop_cycle when project reaches a milestone or completion
# 5. Cycle scripts must end by loading the next cycle
# 6. The stop_cycle is the only cycle that doesn't load another cycle

# Documentation:
# - See meta_cycles/manager_instructions.txt for full documentation
# - See docs/PROJECT_DOCS.md for project architecture
