## **TODO.md**

### **Final Changes & Findings**
1. **Duplicate Constants**:
   - Removed duplicate `MISSING_REQUIRED_FIELD` from `app/constants.py`.
   - Ensured all constants are unique and centralized.

2. **Dependency Conflicts**:
   - Downgraded `Flask` to `2.3.2` to resolve conflicts with `Werkzeug 2.3.7`.

3. **Error Handling**:
   - Enhanced error handling in `app/__init__.py` to catch and log initialization issues.
1. **Dependency Conflicts**:
   - **Issue**: `Flask-Login 0.6.3` is incompatible with `Werkzeug 3.0.1` due to the removal of `url_decode` in `Werkzeug 3.x`.
   - **Fix**: Downgraded `Werkzeug` to `2.3.7` to maintain compatibility with `Flask-Login 0.6.3`.
   - **Lesson**: Always verify compatibility between library versions, especially for critical dependencies like `Flask-Login` and `Werkzeug`.

2. **Missing Constants**:
   - **Issue**: `app/forms/custom_fields.py` imports `MISSING_REQUIRED_FIELD` and `INVALID_DATETIME_FORMAT` from `app/constants.py`, but these constants were missing.
   - **Fix**: Added the following constants to `app/constants.py`:
     ```python
     MISSING_REQUIRED_FIELD = "This field is required."
     INVALID_DATETIME_FORMAT = "Invalid date/time format. Please use YYYY-MM-DD HH:MM:SS."
     ```
   - **Lesson**: Ensure all required constants are defined in `app/constants.py` to avoid `ImportError`.

3. **Testing**:
   - **Issue**: Tests failed due to dependency conflicts and missing constants.
   - **Fix**: Resolved dependency issues and added missing constants, allowing tests to run successfully.
   - **Lesson**: Always run tests after making changes to dependencies or constants to catch issues early.

---

### **Important Info**
1. **Dependencies**:
   - **Key Versions**:
     - `Flask-Login==0.6.3`
     - `Werkzeug==2.3.7`
   - **Reason**: These versions are compatible and avoid the `url_decode` issue.

2. **Constants**:
   - **Location**: `app/constants.py`
   - **Purpose**: Centralized error messages and validation strings for consistency and maintainability.

3. **Testing**:
   - **Command**: `pytest`
   - **Pre-Test Check**: Ensure all dependencies are installed and compatible.

---

### **Things to Remember for Next Coding Session**
1. **Dependency Management**:
   - Always check compatibility between library versions, especially for critical dependencies like `Flask-Login` and `Werkzeug`.
   - Update `requirements.txt` to reflect the correct versions.

2. **Constants**:
   - Use `app/constants.py` for all error messages and validation strings.
   - Verify that all required constants are defined before running the application or tests.

3. **Testing**:
   - Run tests after making changes to dependencies, constants, or validation logic.
   - Use `pytest` for comprehensive testing, including edge cases for date/time validation.

4. **Error Handling**:
   - Log errors with context to facilitate debugging.
   - Provide clear, user-friendly error messages for validation failures.

5. **Code Organization**:
   - Keep validation logic modular and reusable.
   - Avoid hardcoding strings; use constants instead.

---

### **Next Steps**
1. **Verify Dependency Installation**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Run Tests**:
   ```bash
   pytest
   ```
3. **Check Application Routes**:
   ```bash
   flask routes
   ```
