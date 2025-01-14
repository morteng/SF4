# Meta Cycles Project Documentation

## Overview
The Meta Cycles system provides a structured framework for managing software development cycles. It enables automated progression through different development phases while tracking performance metrics and maintaining cycle history.

## Key Components

### Cycle Manager
- Handles cycle transitions and state management
- Maintains cycle history and performance metrics
- Implements error recovery and fallback strategies

### Metrics Collector
- Tracks and analyzes cycle performance
- Enforces resource usage limits
- Provides real-time monitoring capabilities
- Calculates performance scores

### Transition Engine
- Validates cycle prerequisites
- Maintains transition history
- Implements fallback strategies
- Handles error conditions

## Usage Guidelines

### Starting the System
```bash
/load meta_cycles/start.aiderscript
```

### Cycle Transition Rules
1. Each cycle must determine and set the next appropriate cycle
2. Only update the /load directive to point to the next cycle
3. Never add logic or code to cycle files
4. Use stop_cycle when project reaches a milestone or completion
5. Cycle scripts must end by loading the next cycle

### Best Practices
- Keep chooser.aiderscript clean with only /load directives
- Maintain cycle independence and self-containment
- Use dependency management for cross-cycle requirements
- Record metrics before each transition
- Validate dependencies before transitioning

## API Reference
- `/load <cycle>`: Loads the specified cycle
- `/run <script>`: Executes an external script
- `/commit`: Commits current changes to git
- `/add <file>`: Adds file to current context
- `/ask <question>`: Asks the LLM a question
