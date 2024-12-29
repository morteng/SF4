# Updated Coding Conventions

## Setup Instructions

### Pre-Test Verification
Before running tests, the system will automatically verify that all required dependencies are installed. If any dependencies are missing, the test session will abort with a clear error message.

To manually verify dependencies:
```bash
pytest tests/test_dependencies.py
```

### Circular Import Prevention
To avoid circular dependencies:
1. Move shared functionality to `app/common/utils.py`
2. Use lazy imports for dependencies that cannot be refactored
3. Keep imports at the function level when necessary

Example of lazy import:
```python
def some_function():
    from app.services.bot_service import run_bot  # Lazy import
    run_bot()
```

### Property Implementation
All service properties must:
1. Be defined with @property decorator
2. Have a corresponding setter with validation
3. Use private attributes for storage
4. Include docstrings explaining their purpose

### Environment Setup
1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   .venv\Scripts\activate     # On Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Verify critical dependencies:
   ```bash
   pip show freezegun Flask
   ```

4. Run tests:
   ```bash
   pytest
   ```

5. Verify all dependencies are installed:
   ```bash
   pytest tests/test_dependencies.py
   ```

### Troubleshooting

#### Missing Dependencies
If tests fail with `ModuleNotFoundError`:
1. Ensure the virtual environment is activated.
2. Run `pip install -r requirements.txt`.
3. Verify installation with `pip show <package_name>`.

## Troubleshooting

### Missing Dependencies
If tests fail with `ModuleNotFoundError`:
1. Ensure the virtual environment is activated
2. Run `pip install -r requirements.txt`
3. Verify installation with `pip show <package_name>`

### Freezegun Issues
If time-based tests are failing:
1. Ensure freezegun is installed:
   ```bash
   pip show freezegun
   ```
2. If not installed:
   ```bash
   pip install freezegun>=1.2.2
   ```

## Service Layer
- BaseService handles CRUD
- Child services implement domain logic
- Standard method names
- Audit logging via user_id
- Consistent error handling

## Property Implementation Best Practices
1. **Define Properties Correctly**:
   - Always define a property (`@property`) before using a setter (`@<property>.setter`).
   - Example from BaseService implementation:
     ```python
     class BaseService:
         def __init__(self):
             self._create_limit = None

         @property
         def create_limit(self):
             """Getter for create_limit."""
             return self._create_limit

         @create_limit.setter
         def create_limit(self, value):
             """Setter for create_limit."""
             self._create_limit = value
     ```

2. **Avoid Direct Attribute Access**:
   - Use properties to encapsulate attribute access and modification.
   - This ensures consistent behavior and validation.

3. **Document Properties**:
   - Add docstrings to properties and setters to clarify their purpose and behavior.

## Dependency Management
1. **Pre-Test Verification**:
   - Add a test to verify all dependencies are installed before running the test suite.
   - Example:
     ```python
     def test_dependencies():
         try:
             subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
         except subprocess.CalledProcessError:
             pytest.fail("Failed to install dependencies")
     ```

2. **Graceful Handling**:
   - Use try-except blocks to handle missing dependencies in test files.
   - Skip tests that require missing packages instead of failing the entire suite.
   - Always define a property (`@property`) before using a setter (`@<property>.setter`).
   - Example:
     ```python
     class MyClass:
         def __init__(self):
             self._my_property = None

         @property
         def my_property(self):
             return self._my_property

         @my_property.setter
         def my_property(self, value):
             self._my_property = value
     ```

2. **Avoid Direct Attribute Access**:
   - Use properties to encapsulate attribute access and modification.
   - This ensures consistent behavior and validation.

3. **Document Properties**:
   - Add docstrings to properties and setters to clarify their purpose and behavior.

### Circular Imports
- Avoid circular dependencies by refactoring shared functionality into separate modules.
- Use lazy imports or dependency injection where necessary.
1. **Define Properties Correctly**:
   - Always define a property (`@property`) before using a setter (`@<property>.setter`).
   - Example:
     ```python
     class MyClass:
         def __init__(self):
             self._my_property = None

         @property
         def my_property(self):
             return self._my_property

         @my_property.setter
         def my_property(self, value):
             self._my_property = value
     ```

2. **Avoid Direct Attribute Access**:
   - Use properties to encapsulate attribute access and modification.
   - This ensures consistent behavior and validation.

3. **Document Properties**:
   - Add docstrings to properties and setters to clarify their purpose and behavior.

## Validation Best Practices

### Dependency Validation
1. **Issue**: Tests failed because `freezegun` was not installed, even though it was listed in `requirements.txt`.
2. **Solution**:
   - Always install dependencies from `requirements.txt`:
     ```bash
     pip install -r requirements.txt
     ```
   - Verify installation with:
     ```bash
     pip show <package_name>
     ```
3. **Best Practice**:
   - Add a pre-test check to ensure all required dependencies are installed.
   - Document the setup process to avoid similar issues in the future.

### Date/Time Validation
- Always verify the data type of form field inputs before applying validation logic.
- Use `freezegun` to mock the current date/time for deterministic testing
- Verify `freezegun` installation with `pip show freezegun` before running tests
- Handle edge cases like February 29th in non-leap years.
- Validate time components (hours, minutes, seconds) together.

1. **Date/Time Validation**:
   - Validate date and time components separately before full parsing.
   - Use specific error messages for different validation failures (e.g., invalid format, invalid time, invalid leap year).
   - Handle edge cases like February 29th in non-leap years.

2. **Error Handling**:
   - Always use error messages from `app/constants.py` instead of hardcoding them.
   - Provide clear, user-friendly error messages for validation failures.

3. **Testing**:
   - Test all error message variations for validation fields.
   - Verify edge cases in date/time validation (e.g., 25:00:00, February 29th).

4. **Field Initialization**:
   - Avoid passing the same parameter multiple times during field initialization.
   - Use consistent patterns for initializing custom fields.

## Error Handling
- **Centralized Error Messages**:
  - Always use error messages from `app/constants.py` for consistency.
  - Avoid hardcoding error messages in validation logic.

- **Field Initialization**:
  - Ensure parameters are not passed multiple times during field initialization.
  - Use consistent patterns for initializing custom fields.

## Validation Best Practices

1. **Date/Time Validation**:
   - Validate date and time components separately before full parsing.
   - Use specific error messages for different validation failures (e.g., invalid format, invalid time, invalid leap year).
   - Handle edge cases like February 29th in non-leap years.

2. **Error Handling**:
   - Always use error messages from `app/constants.py` instead of hardcoding them.
   - Provide clear, user-friendly error messages for validation failures.

3. **Testing**:
   - Test all error message variations for validation fields.
   - Verify edge cases in date/time validation (e.g., 25:00:00, February 29th).

4. **Field Initialization**:
   - Avoid passing the same parameter multiple times during field initialization.
   - Use consistent patterns for initializing custom fields.

## Error Handling
- Use dict.get() with default messages for error handling
- Centralize common error responses
- Log errors with context before returning user-friendly messages
- Specific exceptions
- Rollback on errors
- Validate inputs
- Preserve exception types

## Validation Best Practices

### Dependency Validation
1. **Issue**: Tests failed because `freezegun` was not installed, even though it was listed in `requirements.txt`.
2. **Solution**:
   - Always install dependencies from `requirements.txt`:
     ```bash
     pip install -r requirements.txt
     ```
   - Verify installation with:
     ```bash
     pip show <package_name>
     ```
3. **Best Practice**:
   - Add a pre-test check to ensure all required dependencies are installed.
   - Document the setup process to avoid similar issues in the future.

### Date/Time Validation
1. **Best Practices**:
   - Validate date and time components separately before full parsing.
   - Use specific error messages for different validation failures (e.g., invalid format, invalid time, invalid leap year).
   - Handle edge cases like February 29th in non-leap years.

2. **Error Handling**:
   - Provide specific error messages for:
     - Invalid date formats.
     - Out-of-range values.
     - Missing required fields.
     - Invalid leap year dates.
     - Invalid time components (hours, minutes, seconds).
   - Use configurable error messages from `app/constants.py`.

3. **Testing**:
   - Test all error message variations for date/time fields.
   - Verify edge cases in date/time validation (e.g., 25:00:00, February 29th).

## Validation Best Practices

### Date/Time Validation Best Practices
1. **Data Type Awareness**:
   - Always verify the data type of form field inputs before applying validation logic.
   - Use `isinstance()` to check for `datetime` objects when working with date/time fields.

2. **Timezone Handling**:
   - Ensure all `datetime` objects are timezone-aware.
   - Use `pytz.UTC.localize()` to add a timezone to naive `datetime` objects.

3. **Future/Past Date Validation**:
   - Validate that dates are within acceptable ranges (e.g., future dates for deadlines).
   - Use `datetime.now(pytz.UTC)` for consistent timezone-aware comparisons.

4. **Error Messages**:
   - Use centralized error messages from `app/constants.py` for consistency.
   - Provide clear, user-friendly error messages for validation failures.

5. **General Validation**:
   - Validate date and time components separately before full parsing.
   - Handle edge cases like February 29th in non-leap years.
   - Test all error message variations for validation fields.
   - Verify edge cases in date/time validation (e.g., 25:00:00, February 29th).
   - Avoid passing the same parameter multiple times during field initialization.
   - Use consistent patterns for initializing custom fields.

## Updated Validation Best Practices

1. **Date/Time Validation**:
   - Validate date and time components separately before full parsing
   - Use specific error messages for different validation failures
   - Handle edge cases like February 29th in non-leap years
   - Validate time components (hours, minutes, seconds) together

2. **Error Handling**:
   - Always use error messages from `app/constants.py`
   - Provide clear, user-friendly error messages
   - Log validation errors with context

3. **Testing**:
   - Test all error message variations
   - Verify edge cases in date/time validation
   - Ensure consistent handling of empty/missing values

### Testing Setup
1. **Dependencies**:
   - Ensure all testing dependencies (e.g., `freezegun`, `pytest`) are installed and up-to-date.
   - Verify installation with `pip show <package_name>`.
   - Install all dependencies:
     ```bash
     pip install -r requirements.txt
     ```

2. **Virtual Environment**:
   - Always activate the virtual environment before running tests or installing dependencies.
   - Use `source .venv/bin/activate` (Linux/Mac) or `.venv\Scripts\activate` (Windows).

3. **Test Execution**:
   - Run tests with `pytest` after ensuring all dependencies are installed.
   - If tests fail due to missing dependencies, install them and re-run the tests.
   - Tests requiring `freezegun` will be skipped if it's not installed, with a clear message.

4. **Dependency Verification**:
   - Check if `freezegun` is installed:
     ```bash
     pip show freezegun
     ```
   - If missing, install it:
     ```bash
     pip install -r requirements.txt
     ```

## Testing Setup

### Dependency Verification
1. **Pre-Test Check**:
   - Add a test to verify all dependencies are installed before running the test suite.
   - Example:
     ```python
     def test_dependencies():
         try:
             subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
         except subprocess.CalledProcessError:
             pytest.fail("Failed to install dependencies")
     ```

2. **Graceful Handling**:
   - Use try-except blocks to handle missing dependencies in test files.
   - Skip tests that require missing packages instead of failing the entire suite.

### Error Handling
- Always use centralized error messages from `app/constants.py`.
- Log validation errors with context for easier debugging.

### Key Takeaways
1. **Validation Logic**:
   - Always verify the data type of form field inputs before applying validation logic.
   - Ensure compatibility with parent classes when overriding attributes or methods.
   - Use centralized error messages from `app/constants.py` for consistency.

2. **Testing**:
   - Test edge cases thoroughly, especially for date/time validation.
   - Use mocking libraries like `freezegun` to ensure deterministic test behavior.

3. **Error Handling**:
   - Log validation errors with context for easier debugging.
   - Provide clear, user-friendly error messages for validation failures.

4. **Code Organization**:
   - Keep validation logic modular and reusable.
   - Avoid code duplication by using base classes and utilities.

## Testing Setup

1. **Dependencies**:
   - Ensure all testing dependencies (e.g., `freezegun`, `pytest`) are installed and up-to-date.
   - Verify installation with `pip show <package_name>`.
   - Install all dependencies:
     ```bash
     pip install -r requirements.txt
     ```

2. **Virtual Environment**:
   - Always activate the virtual environment before running tests or installing dependencies.
   - Use `source .venv/bin/activate` (Linux/Mac) or `.venv\Scripts\activate` (Windows).

3. **Test Execution**:
   - Run tests with `pytest` after ensuring all dependencies are installed.
   - If tests fail due to missing dependencies, install them and re-run the tests.
   - Tests requiring `freezegun` will be skipped if it's not installed, with a clear message.

4. **Dependency Verification**:
   - Check if `freezegun` is installed:
     ```bash
     pip show freezegun
     ```
   - If missing, install it:
     ```bash
     pip install -r requirements.txt
     ```

## Testing Best Practices

### Dependency Verification
1. **Pre-Test Check**:
   - Add a test to verify all dependencies are installed before running the test suite.
   - Example:
     ```python
     def test_dependencies():
         try:
             subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
         except subprocess.CalledProcessError:
             pytest.fail("Failed to install dependencies")
     ```

2. **Graceful Handling**:
   - Use try-except blocks to handle missing dependencies in test files.
   - Skip tests that require missing packages instead of failing the entire suite.

### Error Handling
- Always use centralized error messages from `app/constants.py`.
- Log validation errors with context for easier debugging.

