# Meta Cycles System - Advanced Version

This folder contains an advanced orchestrator that uses the Aider Python API to:
1. Load a `meta_cycle.json` file to find the next pending cycle.
2. Open a single Aider session with the relevant code files.
3. Step through instructions (fix bugs, run tests, fix again, finalize).
4. Mark the cycle "completed" if all tests pass.

## Key Features
- **Cycle Management**: Track cycles with status (pending, in_progress, completed)
- **Priority System**: Higher priority cycles run first
- **File Tracking**: Each cycle tracks which files it affects
- **Test Integration**: Built-in test command execution
- **Audit Trail**: Timestamps for cycle creation and modification

## Setup
1. Install required dependencies:
   ```bash
   pip install aider
   ```
2. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY=sk-XXXX...
   ```
3. Run the orchestrator:
   ```bash
   python meta_cycles/meta_cycle_manager.aiderscript
   ```

## Cycle Configuration
Each cycle in `meta_cycle.json` supports:
- `name`: Descriptive name
- `priority`: Integer priority (higher = more important)
- `status`: Current state (pending/in_progress/completed)
- `script`: Aiderscript to execute
- `target_files`: Files affected by this cycle
- `instructions`: List of tasks to complete
- `test_command`: Command to verify changes
- `created_at`: Timestamp of creation
- `last_modified`: Timestamp of last change

## Usage
1. From the Aider prompt, run:
   ```bash
   /load meta_cycle_manager.aiderscript
   ```
2. The system will:
   - Find the highest priority pending cycle
   - Mark it as in_progress
   - Load the appropriate aiderscript
   - Track progress and completion

Enjoy your fully automated DevOps-coded AI pipeline!
