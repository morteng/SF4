
## Meta Cycles System Architecture

### Core Components
1. **Cycle Manager**
   - Manages cycle transitions and state
   - Tracks cycle history and performance metrics
   - Handles error recovery and fallback cycles
   - Implements automated cycle sequencing
   - Maintains transition history logs

2. **Cycle Executor**
   - Executes individual cycle logic
   - Manages cycle dependencies
   - Handles cycle-specific configurations
   - Tracks resource usage per cycle
   - Implements cycle timeout handling

3. **Metrics Collector**
   - Tracks cycle performance metrics
   - Stores historical data for analysis
   - Provides real-time monitoring
   - Calculates performance scores
   - Enforces resource usage limits

4. **Dependency Manager**
   - Handles cross-cycle dependencies
   - Manages resource allocation
   - Ensures proper sequencing
   - Validates cycle prerequisites
   - Tracks dependency graphs

5. **Transition Engine**
   - Implements cycle transition rules
   - Validates cycle prerequisites
   - Handles error conditions
   - Maintains transition history
   - Implements fallback strategies

### Data Flow
1. Start -> Cycle Manager -> Cycle Executor
2. Cycle Executor -> Metrics Collector -> Transition Engine
3. Transition Engine -> Next Cycle or Stop

### Requirements

#### Functional Requirements
1. Must support at least 30 different cycle types
2. Must track cycle performance metrics
3. Must maintain cycle history
4. Must handle cycle dependencies
5. Must support automated transitions
6. Must provide monitoring capabilities
7. Must support project milestones
8. Must handle error conditions gracefully

#### Non-Functional Requirements
1. Performance: Handle 1000+ cycles per project
2. Scalability: Support multiple concurrent projects
3. Reliability: 99.9% uptime for cycle execution
4. Maintainability: Clear documentation and modular design
5. Security: Role-based access control
6. Extensibility: Easy to add new cycle types
7. Portability: Cross-platform support

## Key Features
- **Modular Cycle System**: Independent, reusable cycle scripts
- **Automated Transitions**: Seamless progression between cycles with sequencing
- **Stop Mechanism**: Controlled project completion
- **Self-Contained**: Easy integration into other projects
- **Documentation**: Complete Aider scripting guide included
- **Monitoring**: Integrated performance tracking
- **Cycle History**: Tracks cycle transitions
- **Performance Metrics**: Cycle performance data
- **Dependency Management**: Automatic handling of cycle dependencies
- **AI Recommendations**: Smart cycle suggestions based on project context
- **Predictive Analytics**: Forecasting system for cycle performance

## Getting Started
1. Initialize the system by running:
   ```bash
   /load meta_cycles/start.aiderscript
   ```
2. The system will automatically progress through appropriate cycles

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
# 2. Only update the /load directive to point to the next cycle
# 3. Never add logic or code to this file
# 4. Use stop_cycle when project reaches a milestone or completion
# 5. Cycle scripts must end by loading the next cycle
# 6. The stop_cycle is the only cycle that doesn't load another cycle

# Supported Cycle Types:
# - Planning
# - Coding
# - Testing
# - Documentation
# - Bugfix
# - Finalize/Cleanup
# - Code Review
# - Deployment
# - Refactoring
# - Research
# - Maintenance
# - Security
# - Performance
# - Infrastructure
# - Integration
# - UI/UX
# - Data
# - Configuration
# - Metrics
# - Monitoring
# - Backup
# - Audit
# - Quality
# - Workflow
# - Migration
# - Dependency
# - Logging
# - Security Audit
# - Design
# - Debugging

# Documentation:
# - See meta_cycles/manager_instructions.txt for full documentation
# - See docs/PROJECT_DOCS.md for project architecture
