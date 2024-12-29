Sir, here’s the consolidated Coding Conventions Guideline—short, sweet, and still full of the good stuff:

---

# Coding Conventions Guideline

## 1. Environment & Dependencies
- **Virtual Environments**: Always activate `.venv` or equivalent before installing/running anything.  
  ```bash
  python -m venv .venv
  source .venv/bin/activate  # macOS/Linux
  .venv\Scripts\activate     # Windows
  ```  
- **Requirements**:  
  - Keep dependencies in `requirements.txt`.  
  - Verify installs with `pip show <package>`.

- **Pre-Test Verification**:  
  ```python
  def test_dependencies():
      try:
          subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
      except subprocess.CalledProcessError:
          pytest.fail("Failed to install dependencies")
  ```
  (Skips tests gracefully if something’s missing—no meltdown required.)

## 2. Testing Setup
- **pytest**: The go-to test runner.
  ```bash
  pip install pytest
  pytest
  ```
- **freezegun**: For controlling date/time in tests without rewriting the space-time continuum, sir.

- **Virtual Environment Recreation** (optional, if your environment spontaneously combusts):
  ```bash
  deactivate
  rm -rf .venv
  python -m venv .venv
  # reactivate and reinstall
  ```

## 3. Custom Field Implementation
- **Handle All Arguments**: If you create a `CustomDateTimeField`, accept all typical field arguments.
- **Default Validators**: If `validators` is `None`, default to `[InputRequired()]`.
  ```python
  if validators is None:
      validators = [InputRequired()]
  ```
- **Usage**: Avoid passing in the `validators` argument again unless it’s truly necessary.

## 4. Property Implementation
- **@property** before `@<property>.setter`:  
  ```python
  @property
  def create_limit(self):
      return self._create_limit

  @create_limit.setter
  def create_limit(self, value):
      self._create_limit = value
  ```
- **No Direct `_attribute` Access**: Keep logic consistent (and your code less feral).

- **Docstrings**: Because future you will forget what that property was for, sir.

## 5. Circular Imports
- **Refactor Shared Logic**: Dump it into `common/utils.py` or something equally central.  
- **Lazy Imports**: Import from dependent modules inside functions if you must. That way your code doesn’t eat itself alive.

## 6. Validation Best Practices
- **General**: Verify input types before applying any fancy logic.  
- **Date/Time**:  
  - Validate date/time components individually.  
  - Watch for leap-year shenanigans.  
  - Use `freezegun` to test predictable moments in time.  
- **Error Messages**: Centralize in `app/constants.py` so you don’t sprinkle random strings all over.

## 7. Error Handling & Organization
- **Centralized Errors**: Single source of truth for messages, making your logs (and your sanity) that much better.
- **Graceful Fails**: If a package is missing, skip the test. Don’t throw the entire test suite off the cliff.  
- **Modular Code**: Minimal duplication, maximum reusability. Keep your code as neat as your desk (or neater, sir).

---

That’s it, sir. Implement these guidelines and you’ll have cleaner code, fewer headaches, and more time to sip tea while the tests run successfully. Enjoy!