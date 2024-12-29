# Updated Coding Conventions

## Testing Setup

### 1. Install pytest
1. Activate virtual environment:
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`
2. Install pytest:
   ```bash
   pip install pytest
   ```
3. Verify installation:
   ```bash
   pip show pytest
   ```
4. Add to requirements.txt:
   ```bash
   echo "pytest" >> requirements.txt
   ```

### 2. Fix CustomDateTimeField
Update initialization to handle validators correctly:
```python
class CustomDateTimeField(Field):
    def __init__(self, label=None, validators=None, **kwargs):
        if validators is None:
            validators = [InputRequired()]
        super().__init__(label=label, validators=validators, **kwargs)
```

### 3. Resolve Circular Imports
1. Create shared utils module:
   ```bash
   mkdir -p app/common
   touch app/common/utils.py
   ```
2. Move shared code to app/common/utils.py
3. Use lazy imports where needed:
   ```python
   def some_function():
       from app.services.bot_service import run_bot
       run_bot()
   ```

### 4. Dependency Verification
Add pre-test check:
```python
def test_dependencies():
    try:
        subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError:
        pytest.fail("Failed to install dependencies")
```

### 5. Property Implementation
When implementing properties in Python:
1. Always define a property (`@property`) before using a setter (`@<property>.setter`)
2. Include validation in setters
3. Use private attributes for storage
4. Example:
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

### 5. Centralize Error Messages
Define messages in app/constants.py:
```python
INVALID_DATE_FORMAT = "Invalid date format. Please use YYYY-MM-DD HH:MM:SS."
MISSING_REQUIRED_FIELD = "This field is required."
```

## Testing Setup

#### 1. Fix `pytest` Installation
1. Activate your virtual environment:
   - **Windows**: `.venv\Scripts\activate`
   - **macOS/Linux**: `source .venv/bin/activate`

2. Install `pytest`:
   ```bash
   pip install pytest
   ```

3. Verify the installation:
   ```bash
   pip show pytest
   ```

4. Add `pytest` to `requirements.txt`:
   ```bash
   echo "pytest" >> requirements.txt
   ```

#### 2. Fix `CustomDateTimeField` Initialization
1. Locate the `CustomDateTimeField` class (likely in `app/forms/admin_forms.py` or similar).

2. Replace the existing implementation with the corrected version:
   ```python
   from wtforms import Field
   from wtforms.validators import InputRequired

   class CustomDateTimeField(Field):
       def __init__(self, label=None, validators=None, **kwargs):
           if validators is None:
               validators = [InputRequired()]  # Default validator
           super().__init__(label=label, validators=validators, **kwargs)
   ```

3. Update forms using `CustomDateTimeField` to avoid passing `validators` explicitly unless needed. For example, in `StipendForm`:
   ```python
   application_deadline = CustomDateTimeField("Application Deadline", format="%Y-%m-%d %H:%M:%S")
   ```

#### 3. Run the Tests
1. Activate your virtual environment (if not already activated):
   - **Windows**: `.venv\Scripts\activate`
   - **macOS/Linux**: `source .venv/bin/activate`

2. Run the tests:
   ```bash
   pytest
   ```

#### 4. Optional: Add Dependency Verification
To avoid missing dependencies in the future, add a pre-test check in a file like `tests/test_dependencies.py`:
```python
import subprocess
import pytest

def test_dependencies():
    try:
        subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError:
        pytest.fail("Failed to install dependencies")
```

### Dependency Verification
1. **Pre-Test Check**:
   - Add a test to verify all dependencies are installed before running the test suite:
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

### Installation and Verification
1. Activate your virtual environment:
   - **Windows**: `.venv\Scripts\activate`
   - **macOS/Linux**: `source .venv/bin/activate`
2. Install `pytest`:
   ```bash
   pip install pytest
   ```
3. Verify the installation:
   ```bash
   pip show pytest
   ```
4. Add `pytest` to `requirements.txt`:
   ```bash
   echo "pytest" >> requirements.txt
   ```
5. Run tests:
   ```bash
   pytest
   ```

### Dependency Verification
1. **Pre-Test Check**:
   - Add a test to verify all dependencies are installed before running the test suite:
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

### Custom Field Implementation
1. **Handle All Arguments**:
   - Ensure custom fields properly handle all arguments passed to them (e.g., `validators`).
2. **Default Validators**:
   - Provide default validators if none are passed:
     ```python
     if validators is None:
         validators = [InputRequired()]
     ```

### Installation and Verification
1. Activate your virtual environment:
   - **Windows**: `.venv\Scripts\activate`
   - **macOS/Linux**: `source .venv/bin/activate`

2. Install `pytest`:
   ```bash
   pip install pytest
   pip show pytest
   ```

3. Add `pytest` to `requirements.txt`:
   ```bash
   echo "pytest" >> requirements.txt
   ```

4. Install all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Verify critical packages:
   ```bash
   pip show pytest freezegun Flask
   ```

6. Run tests:
   ```bash
   pytest
   ```

7. If tests fail due to missing dependencies:
   ```bash
   pip install -r requirements.txt
   pytest
   ```

8. Recreate virtual environment (if needed):
   ```bash
   deactivate
   rm -rf .venv
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   pytest
   ```

### Fixing CustomDateTimeField Initialization
1. Locate the `CustomDateTimeField` class (likely in `app/forms/admin_forms.py` or similar)
2. Replace with:
   ```python
   from wtforms import Field
   from wtforms.validators import InputRequired

   class CustomDateTimeField(Field):
       def __init__(self, label=None, validators=None, **kwargs):
           if validators is None:
               validators = [InputRequired()]  # Default validator
           super().__init__(label=label, validators=validators, **kwargs)
   ```
3. Update forms using `CustomDateTimeField` to avoid passing `validators` explicitly unless needed:
   ```python
   application_deadline = CustomDateTimeField("Application Deadline", format="%Y-%m-%d %H:%M:%S")
   ```

### **5. Add Pre-Test Dependency Verification**
1. Create a test file (e.g., `tests/test_dependencies.py`) with the following content:
   ```python
   import subprocess
   import pytest

   def test_dependencies():
       try:
           subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
       except subprocess.CalledProcessError:
           pytest.fail("Failed to install dependencies")
   ```
2. Run the test to verify dependencies:
   ```bash
   pytest tests/test_dependencies.py
   ```

2. **Graceful Handling**:
   - Use try-except blocks to handle missing dependencies in test files.
   - Skip tests that require missing packages instead of failing the entire suite.

### **2. Fix `CustomDateTimeField` Initialization**
1. Locate the `CustomDateTimeField` class in your codebase (likely in `app/forms/admin_forms.py` or a similar file).
2. Replace the existing implementation with the corrected version:
   ```python
   from wtforms import Field
   from wtforms.validators import InputRequired

   class CustomDateTimeField(Field):
       def __init__(self, label=None, validators=None, **kwargs):
           if validators is None:
               validators = [InputRequired()]  # Default validator
           super().__init__(label=label, validators=validators, **kwargs)
   ```
3. Ensure that the `StipendForm` class (or any other form using `CustomDateTimeField`) does not pass the `validators` argument explicitly unless necessary. For example:
   ```python
   application_deadline = CustomDateTimeField("Application Deadline", format="%Y-%m-%d %H:%M:%S")
   ```

## Testing Setup

### Installation and Verification
1. Install pytest:
   ```bash
   pip install pytest
   pip show pytest
   ```

2. Install all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Verify critical packages:
   ```bash
   pip show pytest freezegun Flask
   ```

4. Run tests:
   ```bash
   pytest
   ```

### CustomDateTimeField Implementation
The `CustomDateTimeField` class must handle the `validators` argument correctly:
```python
class CustomDateTimeField(Field):
    def __init__(self, label=None, validators=None, **kwargs):
        if validators is None:
            validators = [InputRequired()]  # Default validator
        super().__init__(label=label, validators=validators, **kwargs)
```

### **3. Fix Circular Imports**
1. Identify the circular import chain. For example:
   ```
   app/__init__.py → app/routes/admin/user_routes.py → app/forms/admin_forms.py → app/__init__.py
   ```
2. Refactor shared functionality into a separate module (e.g., `app/common/utils.py`). For example:
   ```python
   # app/common/utils.py
   def init_admin_user():
       # Implementation
       pass
   ```
3. Use lazy imports where necessary. For example:
   ```python
   # app/routes/admin/user_routes.py
   def some_function():
       from app.services.bot_service import run_bot  # Lazy import
       run_bot()
   ```

### Dependency Verification
1. **Pre-Test Check**:
   - Add a test to verify all dependencies are installed before running the test suite:
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

### Property Implementation
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

### Testing Setup
1. **Install pytest**:
   ```bash
   pip install pytest
   pip show pytest
   echo "pytest" >> requirements.txt
   pytest
   ```

2. **Dependency Verification**:
   - Add a pre-test check to ensure all required dependencies are installed:
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

### Property Implementation
1. **Define Properties Correctly**:
   - Always define a property (`@property`) before using a setter (`@<property>.setter`).
   - Example:
     ```python
     class BaseService:
         def __init__(self):
             self._create_limit = None

         @property
         def create_limit(self):
             return self._create_limit

         @create_limit.setter
         def create_limit(self, value):
             self._create_limit = value
     ```

2. **Avoid Direct Attribute Access**:
   - Use properties to encapsulate attribute access and modification.

3. **Document Properties**:
   - Add docstrings to properties and setters to clarify their purpose and behavior.

### Circular Imports
1. **Refactor Shared Functionality**:
   - Move shared code to a separate module (e.g., `app/common/utils.py`).
2. **Use Lazy Imports**:
   - Import dependencies at the function level when necessary:
     ```python
     def some_function():
         from app.services.bot_service import run_bot  # Lazy import
         run_bot()
     ```

### Key Takeaways
- **Validation Logic**: Always verify the data type of form field inputs before applying validation logic.
- **Testing**: Test edge cases thoroughly, especially for date/time validation.
- **Error Handling**: Log validation errors with context for easier debugging.
- **Code Organization**: Keep validation logic modular and reusable.

#### Validation Testing
- Added comprehensive tests for edge cases in `tests/test_validation.py`
- Uses `freezegun` for deterministic time-based testing
- Tests include:
  - Leap year validation
  - Invalid time validation
  - Centralized error message handling

### **1. Fix `pytest` Installation**
1. Activate your virtual environment:
   - **Windows**: `.venv\Scripts\activate`
   - **macOS/Linux**: `source .venv/bin/activate`
2. Install `pytest`:
   ```bash
   pip install pytest
   ```
3. Verify the installation:
   ```bash
   pip show pytest
   ```
4. Add `pytest` to `requirements.txt`:
   ```bash
   echo "pytest" >> requirements.txt
   ```
   If installed correctly, you'll see details about the `pytest` package.

#### 4. Add `pytest` to `requirements.txt`
   Add `pytest` to your `requirements.txt` file to ensure it's installed in the future:
   ```bash
     echo "pytest" >> requirements.txt
   ```

#### 5. Run Tests
   After installing `pytest`, run the tests:
   ```bash
     pytest
   ```

#### 6. Optional: Install All Dependencies
   If other dependencies are missing, install them using:
   ```bash
     pip install -r requirements.txt
   ```

#### 7. Recreate Virtual Environment (if needed)
   If the issue persists, recreate the virtual environment:
   ```bash
     deactivate
     rm -rf .venv
     python -m venv .venv
     source .venv/bin/activate  # macOS/Linux
     .venv\Scripts\activate     # Windows
     pip install -r requirements.txt
     pytest
   ```

#### Expected Outcome:
After following these steps, the `pytest` command should work without errors, and your tests should run successfully.

#### **Property Implementation**
1. **Define Properties Correctly**:
   - Always define a property (`@property`) before using a setter (`@<property>.setter`).
   - Example:
     ```python
     class BaseService:
         def __init__(self):
             self._create_limit = None

         @property
         def create_limit(self):
             return self._create_limit

         @create_limit.setter
         def create_limit(self, value):
             self._create_limit = value
     ```

2. **Avoid Direct Attribute Access**:
   - Use properties to encapsulate attribute access and modification.

3. **Document Properties**:
   - Add docstrings to properties and setters to clarify their purpose and behavior.

#### **Circular Imports**
1. **Refactor Shared Functionality**:
   - Move shared code to a separate module (e.g., `app/common/utils.py`).
2. **Use Lazy Imports**:
   - Import dependencies at the function level when necessary:
     ```python
     def some_function():
         from app.services.bot_service import run_bot  # Lazy import
         run_bot()
     ```
### **6. Run the Tests**
After implementing the fixes, run the tests again:
```bash
pytest
```

### **Expected Outcome**
- The `pytest` command should execute without errors.
- All tests should pass, and the `flask routes` command should work correctly.

### Property Implementation
1. **Define Properties Correctly**:
   - Always define a property (`@property`) before using a setter (`@<property>.setter`).
   - Example:
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

### Dependency Management
1. **Pre-Test Verification**:
   - Add a test to verify all dependencies are installed before running the test suite:
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

### Circular Imports
1. **Refactor Shared Functionality**:
   - Move shared code to a separate module (e.g., `app/common/utils.py`).
2. **Use Lazy Imports**:
   - Import dependencies at the function level when necessary:
     ```python
     def some_function():
         from app.services.bot_service import run_bot  # Lazy import
         run_bot()
     ```

### Custom Field Implementation
1. **Handle All Arguments**:
   - Ensure custom fields properly handle all arguments passed to them (e.g., `validators`).
   - Provide default validators if none are passed:
     ```python
     if validators is None:
         validators = [InputRequired()]  # Default validator
     ```
2. **Default Validators**:
   - Provide default validators if none are passed:
     ```python
     if validators is None:
         validators = [InputRequired()]
     ```

### Key Takeaways
- **Validation Logic**: Always verify the data type of form field inputs before applying validation logic.
- **Testing**: Test edge cases thoroughly, especially for date/time validation.
- **Error Handling**: Log validation errors with context for easier debugging.
- **Code Organization**: Keep validation logic modular and reusable.

## Setup Instructions

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

### Pre-Test Verification
Before running tests, the system will automatically verify that all required dependencies are installed. If any dependencies are missing, it will attempt to install them before skipping affected tests.

To verify dependencies, run:
```bash
pytest tests/test_dependencies.py
```

Example implementation:
```python
import pytest
import importlib

def verify_dependencies():
    missing_deps = []
    for dep in ["pytest", "freezegun", "Flask"]:
        try:
            importlib.import_module(dep)
        except ImportError:
            missing_deps.append(dep)
    if missing_deps:
        pytest.skip(f"Missing dependencies: {', '.join(missing_deps)}")
```

```python
import subprocess
import pytest
import importlib

def verify_dependencies():
    missing_deps = []
    for dep in ["freezegun", "Flask"]:
        try:
            importlib.import_module(dep)
        except ImportError:
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"Attempting to install missing dependencies: {', '.join(missing_deps)}")
        try:
            subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
        except subprocess.CalledProcessError:
            pytest.skip(f"Missing dependencies: {', '.join(missing_deps)}")
```

To manually verify dependencies:
```bash
pip install -r requirements.txt
pip show freezegun Flask
pytest tests/test_dependencies.py
```

Example dependency verification function:
```python
import subprocess
import pytest
import importlib

def verify_dependencies():
    missing_deps = []
    for dep in ["freezegun", "Flask"]:
        try:
            importlib.import_module(dep)
        except ImportError:
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"Attempting to install missing dependencies: {', '.join(missing_deps)}")
        try:
            subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
        except subprocess.CalledProcessError:
            pytest.skip(f"Missing dependencies: {', '.join(missing_deps)}")
```

### Dependency Verification
1. Install required dependencies:
```bash
pip install pytest freezegun Flask
```

2. Verify installation:
```bash
pip show pytest freezegun Flask
```

3. Run tests:
```bash
pytest
```

4. If tests fail due to missing dependencies:
```bash
pip install -r requirements.txt
pytest
```

### Circular Import Prevention
To avoid circular dependencies:
1. Move shared functionality to `app/common/utils.py`
2. Use lazy imports for dependencies that cannot be refactored
3. Example:
   ```python
   # Move shared code to app/common/utils.py
   def init_admin_user():
       # Implementation
       pass

   # Example lazy import
   def some_function():
       from app.services.bot_service import run_bot  # Lazy import
       run_bot()
   ```
3. Example:
   ```python
   def some_function():
       from app.services.bot_service import run_bot  # Lazy import
       run_bot()
   ```

### Property Implementation
1. Always define a property (`@property`) before using a setter (`@<property>.setter`)
2. Include validation in setters and use private attributes for storage

### Dependency Management
1. Add a pre-test check to ensure all required dependencies are installed
2. Example:
   ```python
   def test_dependencies():
       try:
           subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
       except subprocess.CalledProcessError:
           pytest.fail("Failed to install dependencies")
   ```
2. Use lazy imports for dependencies that cannot be refactored
3. Keep imports at the function level when necessary
4. Example refactoring:
   ```python
   # Move shared code to app/common/utils.py
   def init_admin_user():
       # Implementation
       pass
   ```
5. Example lazy import:
   ```python
   def some_function():
       from app.services.bot_service import run_bot  # Lazy import
       run_bot()
   ```

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

1. **Activate the Virtual Environment**:
   - **Windows**:
     ```bash
     .venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source .venv/bin/activate
     ```

2. **Install `pytest`**:
   ```bash
   pip install pytest
   ```

3. **Verify Installation**:
   ```bash
   pip show pytest
   ```

4. **Run Tests**:
   ```bash
   pytest
   ```

5. **Add `pytest` to `requirements.txt` (Optional)**:
   ```bash
   echo "pytest" >> requirements.txt
   ```

6. **Install All Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

7. **Verify Virtual Environment**:
   - Check Python path:
     ```bash
     which python  # macOS/Linux
     where python  # Windows
     ```
   - This should point to the Python executable inside your `.venv` directory.

8. **Recreate Virtual Environment (Optional)**:
   ```bash
   deactivate
   rm -rf .venv
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

9. **Verify Critical Packages**:
   ```bash
   pip show freezegun Flask pytest
   ```

10. **Run Dependency Verification Test**:
    ```bash
    pytest tests/test_dependencies.py
    ```

#### Fixing CustomDateTimeField Errors
If you encounter `TypeError: CustomDateTimeField.__init__() got an unexpected keyword argument 'validators'`:

1. Update the `CustomDateTimeField` class:
   ```python
   from wtforms import Field
   from wtforms.validators import InputRequired

   class CustomDateTimeField(Field):
       def __init__(self, label=None, validators=None, **kwargs):
           if validators is None:
               validators = [InputRequired()]  # Default validator
           super().__init__(label=label, validators=validators, **kwargs)
   ```

2. Update the `StipendForm` class:
   ```python
   from flask_wtf import FlaskForm
   from wtforms.validators import InputRequired

   class StipendForm(FlaskForm):
       application_deadline = CustomDateTimeField(
           "Application Deadline",
           format="%Y-%m-%d %H:%M:%S",
           validators=[InputRequired()]  # Explicitly pass validators
       )
   ```

3. Run tests again:
   ```bash
   pytest
   ```

## Troubleshooting

### Missing Dependencies
If tests fail with `ModuleNotFoundError`:

1. **Activate the Virtual Environment**:
   - **Windows**:
     ```bash
     .venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source .venv/bin/activate
     ```

2. **Install `pytest`**:
   ```bash
   pip install pytest
   ```

3. **Verify Installation**:
   ```bash
   pip show pytest
   ```

4. **Install All Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run Tests**:
   ```bash
   pytest
   ```

6. **Recreate Virtual Environment (Optional)**:
   ```bash
   deactivate
   rm -rf .venv
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

7. **Add `pytest` to `requirements.txt` (Optional)**:
   ```bash
   echo "pytest" >> requirements.txt
   ```

8. **Verify Critical Packages**:
   ```bash
   pip show pytest freezegun Flask
   ```

9. **Run Dependency Verification Test**:
   ```bash
   pytest tests/test_dependencies.py
   ```

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
   - Always define a property (`@property`) before using a setter (`@<property>.setter`)
   - Include validation in setters
   - Use private attributes for storage
   - Include docstrings explaining their purpose
   - Example from BaseService implementation with validation:
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

### Dependency Management
1. **Pre-Test Verification**:
   - Add pre-test verification of dependencies
   - Use try-except blocks to handle missing dependencies gracefully
   - Example test:
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

## Best Practices

### Custom Field Implementation
1. **Handle All Arguments**:
   - Ensure custom fields properly handle all arguments passed to them (e.g., `validators`).
2. **Default Validators**:
   - Provide default validators if none are passed:
     ```python
     if validators is None:
         validators = [InputRequired()]
     ```

### Dependency Management
1. **Pre-Test Verification**:
   - Add a pre-test check to ensure all required dependencies are installed:
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

### Circular Imports
1. **Refactor Shared Functionality**:
   - Move shared code to a separate module (e.g., `app/common/utils.py`).
2. **Use Lazy Imports**:
   - Import dependencies at the function level when necessary:
     ```python
     def some_function():
         from app.services.bot_service import run_bot  # Lazy import
         run_bot()
     ```

### Property Implementation
1. **Define Properties Correctly**:
   - Always define a property (`@property`) before using a setter (`@<property>.setter`).
2. **Avoid Direct Attribute Access**:
   - Use properties to encapsulate attribute access and modification.
3. **Document Properties**:
   - Add docstrings to properties and setters to clarify their purpose and behavior.

### Custom Field Implementation
1. **Handle All Arguments**:
   - Ensure custom fields properly handle all arguments passed to them (e.g., `validators`).
2. **Default Validators**:
   - Provide default validators if none are passed:
     ```python
     if validators is None:
         validators = [InputRequired()]
     ```

### Dependency Management
1. **Pre-Test Verification**:
   - Add a pre-test check to ensure all required dependencies are installed:
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

### Circular Imports
1. **Refactor Shared Functionality**:
   - Move shared code to a separate module (e.g., `app/common/utils.py`).
2. **Use Lazy Imports**:
   - Import dependencies at the function level when necessary:
     ```python
     def some_function():
         from app.services.bot_service import run_bot  # Lazy import
         run_bot()
     ```

### Property Implementation
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
3. **Document Properties**:
   - Add docstrings to properties and setters to clarify their purpose and behavior.

### Custom Field Implementation
1. **Handle All Arguments**:
   - Ensure custom fields properly handle all arguments passed to them (e.g., `validators`).
2. **Default Validators**:
   - Provide default validators if none are passed:
     ```python
     if validators is None:
         validators = [InputRequired()]
     ```

### Circular Import Prevention
1. **Refactor Shared Functionality**:
   - Move shared code to a separate module (e.g., `app/common/utils.py`).
2. **Use Lazy Imports**:
   - Import dependencies at the function level when necessary:
     ```python
     def some_function():
         from app.services.bot_service import BotService  # Lazy import
         bot_service = BotService()
     ```

### Dependency Verification
1. **Pre-Test Check**:
   - Add a test to verify all dependencies are installed before running the test suite:
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

### Error Message Centralization
1. **Constants File**:
   - Store all error messages in `app/constants.py`.
2. **Consistency**:
   - Use constants instead of hardcoded strings for error messages.

### Dependency Management
1. **Pre-Test Verification**:
   - Add a test to verify all dependencies are installed before running the test suite:
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

### Property Implementation
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
3. **Document Properties**:
   - Add docstrings to properties and setters to clarify their purpose and behavior.

### Circular Imports
1. **Refactor Shared Functionality**:
   - Move shared code to a separate module (e.g., `app/common/utils.py`).
2. **Use Lazy Imports**:
   - Import dependencies at the function level when necessary:
     ```python
     def some_function():
         from app.services.bot_service import BotService  # Lazy import
         bot_service = BotService()
     ```

### Custom Field Implementation
1. **Handle All Arguments**:
   - Ensure custom fields properly handle all arguments passed to them (e.g., `validators`).
2. **Default Validators**:
   - Provide default validators if none are passed:
     ```python
     if validators is None:
         validators = [InputRequired()]
     ```
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
3. **Document Properties**:
   - Add docstrings to properties and setters to clarify their purpose and behavior.

### Date/Time Validation
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

### General Validation
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

### Circular Import Prevention
1. **Refactor Shared Functionality**:
   - Move shared code to a separate module (e.g., `app/common/utils.py`).
2. **Use Lazy Imports**:
   - Import dependencies at the function level when necessary:
     ```python
     def some_function():
         from app.services.bot_service import BotService  # Lazy import
         bot_service = BotService()
     ```

### Dependency Management
1. **Pre-Test Verification**:
   - Add a test to verify all dependencies are installed before running the test suite:
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

### Property Implementation
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
3. **Document Properties**:
   - Add docstrings to properties and setters to clarify their purpose and behavior.

### Date/Time Validation
1. **Data Type Awareness**:
   - Always verify the data type of form field inputs before applying validation logic.
2. **Timezone Handling**:
   - Ensure all `datetime` objects are timezone-aware.
3. **Future/Past Date Validation**:
   - Validate that dates are within acceptable ranges (e.g., future dates for deadlines).
4. **Error Messages**:
   - Use centralized error messages from `app/constants.py` for consistency.

### General Validation
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

### Circular Imports
1. **Refactor Shared Functionality**:
   - Move shared code to a separate module (e.g., `app/common/utils.py`).
2. **Use Lazy Imports**:
   - Import dependencies at the function level when necessary:
     ```python
     def some_function():
         from app.services.bot_service import BotService  # Lazy import
         bot_service = BotService()
     ```

### Property Implementation
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
3. **Document Properties**:
   - Add docstrings to properties and setters to clarify their purpose and behavior.

### Dependency Management
1. **Pre-Test Verification**:
   - Add a test to verify all dependencies are installed before running the test suite:
     ```python
     def test_dependencies():
         try:
             subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
         except subprocess.CalledProcessError:
             pytest.fail("Failed to install dependencies")
     ```
2. **Graceful Handling**:
   - Skip tests that require missing packages instead of failing the entire suite.

### Property Implementation
1. **Define Properties Correctly**:
   Always define a property (`@property`) before using a setter (`@<property>.setter`).
   Example:
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
   Use properties to encapsulate attribute access and modification.
3. **Document Properties**:
   Add docstrings to properties and setters to clarify their purpose and behavior.

### Package Structure
1. **`__init__.py` Files**:
   Always include `__init__.py` in directories to make them recognizable as Python packages.

2. **Avoid Circular Imports**:
   Refactor shared functionality into separate modules (e.g., `app/common/utils.py`) and use lazy imports where necessary.

### Testing
1. **Graceful Handling**:
   Skip tests that require missing dependencies instead of failing the entire suite.

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

### Date/Time Validation
1. **Data Type Awareness**:
   - Always verify the data type of form field inputs before applying validation logic.
2. **Timezone Handling**:
   - Ensure all `datetime` objects are timezone-aware.
3. **Future/Past Date Validation**:
   - Validate that dates are within acceptable ranges (e.g., future dates for deadlines).
4. **Error Messages**:
   - Use centralized error messages from `app/constants.py` for consistency.

### Custom Field Implementation
1. **Handle All Arguments**:
   - Ensure custom fields properly handle all arguments passed to them (e.g., `validators`).
2. **Default Validators**:
   - Provide default validators if none are passed:
     ```python
     if validators is None:
         validators = [InputRequired()]
     ```

### General Validation
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

#### 1. Activate the Virtual Environment
   - **Windows**:
     ```bash
     .venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source .venv/bin/activate
     ```

#### 2. Install `pytest`
   Run this command to install `pytest`:
   ```bash
   pip install pytest
   ```

#### 3. Verify Installation
   Confirm `pytest` is installed by running:
   ```bash
   pip show pytest
   ```
   If installed correctly, you'll see details about the `pytest` package.

#### 4. Add `pytest` to `requirements.txt`
   Add `pytest` to your `requirements.txt` file to ensure it's installed in the future:
   ```bash
   echo "pytest" >> requirements.txt
   ```

#### 5. Run Tests
   After installing `pytest`, run the tests:
   ```bash
   pytest
   ```

#### 6. Optional: Install All Dependencies
   If other dependencies are missing, install them using:
   ```bash
   pip install -r requirements.txt
   ```

#### 7. Recreate Virtual Environment (if needed)
   If the issue persists, recreate the virtual environment:
   ```bash
   deactivate
   rm -rf .venv
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   pytest
   ```

#### Expected Outcome:
After following these steps, the `pytest` command should work without errors, and your tests should run successfully.

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

### Troubleshooting pytest Issues
1. **Activate Virtual Environment**:
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`

2. **Install pytest**:
   ```bash
   pip install pytest
   ```

3. **Verify Installation**:
   ```bash
   pip show pytest
   ```

4. **Run Tests**:
   ```bash
   pytest
   ```

5. **Optional: Install All Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

6. **Recreate Virtual Environment (if needed)**:
   ```bash
   deactivate
   rm -rf .venv
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```

7. **Run Tests Again**:
   ```bash
   pytest
   ```

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

## Property Implementation
- Always define properties with `@property` and `@<property>.setter`
- Include validation in setters
- Use private attributes for storage

## Dependency Management
- Add pre-test verification of dependencies
- Skip tests gracefully if dependencies are missing

## Date/Time Validation
- Validate date and time components separately
- Handle edge cases like leap years
- Use centralized error messages from `app/constants.py`
