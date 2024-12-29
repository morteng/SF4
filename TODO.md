# Todo
1. fix tests
2. update this list with new actionable items

### **Things to Remember for Next Coding Session**
1. **Error Handling**:
   - Always include proper error handling for `try` blocks to avoid syntax errors.
   - Log errors with context to facilitate debugging.

2. **Constants Management**:
   - Use `app/constants.py` for all error messages and validation strings.
   - Verify that all required constants are defined and imported correctly.

3. **Dependency Management**:
   - Always check compatibility between library versions, especially for critical dependencies like `Flask-Login` and `Werkzeug`.
   - Update `requirements.txt` to reflect the correct versions.

4. **Testing**:
   - Run tests after making changes to dependencies, constants, or validation logic.
   - Use `pytest` for comprehensive testing, including edge cases for date/time validation.

5. **Code Organization**:
   - Keep validation logic modular and reusable.
   - Avoid hardcoding strings; use constants instead.


### **Lessons Learned**
1. **Proper Error Handling**:
   - Always include `except` or `finally` blocks for `try` statements to avoid syntax errors.

2. **Centralized Constants**:
   - Keeping all error messages and validation strings in `app/constants.py` ensures consistency and reduces the chance of typos.

3. **Dependency Verification**:
   - Verify dependencies before running tests to avoid installation issues.

4. **Testing Edge Cases**:
   - Pay special attention to edge cases for date/time validation, such as leap years and invalid time components.

