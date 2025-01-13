# Cycle Rules

1. **Structure**
   - Name, Objectives, Steps, Exit Criteria, Completed Status.

2. **Flexibility**
   - Steps can be reorganized if test results require a re-run or refactor cycle midstream.

3. **Command Injections**
   - Use `dynamic_command_executor.py` to insert or remove console commands based on test outcomes or coverage.

4. **Validation**
   - Before marking `completed = true`, ensure all exit criteria are met, including stable tests.
