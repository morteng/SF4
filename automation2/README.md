# Automation2 System

## Overview
This system is an extension of the original automation workflow in your project. It introduces:
- **Meta-cycles** for dynamic prioritization (e.g., bug fixes vs. new features).
- **Conditional command execution** based on test results, coverage, etc.
- **Centralized context management** for communication between cycles.

## Structure
- **rules/**: Holds global, meta-cycle, and per-cycle guidelines.
- **scripts/**: Contains Python scripts for logic and utilities.
- **cycles/**: JSON files for meta-cycle definitions, templates, and current state tracking.
- **logs/**: Contains logs and metrics (like test coverage, performance data).
- **templates/**: Holds text and JSON templates for new cycles and tasks.

## Usage
1. Edit `meta_cycle.json` to define or reorder your cycles by priority.
2. Run `meta_cycle_manager.py` to select or create the next cycle.
3. Watch the logs in `logs/cycle_metrics.log` or run other scripts to maintain the system.

## Getting Started
```bash
cd automation2
python scripts/meta_cycle_manager.py
```

That's it! Let the AI system handle the rest.
