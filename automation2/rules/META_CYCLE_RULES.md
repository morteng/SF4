# Meta-Cycle Rules

1. **Priority-Driven Selection**
   - Cycles are selected based on priority, highest first.
   - If multiple cycles share the same priority, pick the first found or rely on custom logic.

2. **Escalation**
   - If a cycle stalls or fails, escalate to the manager for immediate review.

3. **Completion Updates**
   - A cycle must be marked as `completed` in `meta_cycle.json` when finished.
   - `meta_cycle_manager.py` then moves on to the next highest-priority cycle.

4. **Logging & Tracking**
   - Write an entry to `logs/cycle_metrics.log` upon cycle completion, including:
     - Time taken
     - Test pass/fail stats
     - Notable issues
