# Coding Conventions Guideline

## 1. Environment & Dependencies
    
- **Requirements**:  
  - Keep dependencies in `requirements.txt`.  

- **Pre-Test Verification**:  
  python
  def test_dependencies():
      try:
          subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
      except subprocess.CalledProcessError:
          pytest.fail("Failed to install dependencies")
  
  (Skips tests gracefully if something’s missing—no meltdown required.)

## 2. Testing Setup
- **pytest**   
- **freezegun**: For controlling date/time in tests.


## 3. Custom Field Implementation
- **Handle All Arguments**: If you create a `CustomDateTimeField`, accept all typical field arguments.
- **Default Validators**: If `validators` is `None`, default to `[InputRequired()]`.
  
  if validators is None:
      validators = [InputRequired()]
  
- **Usage**: Avoid passing in the `validators` argument again unless it’s truly necessary.

## 4. Property Implementation
- **@property** before `@<property>.setter`:  
  
  @property
  def create_limit(self):
      return self._create_limit

  @create_limit.setter
  def create_limit(self, value):
      self._create_limit = value
  
- **No Direct `_attribute` Access**: Keep logic consistent (and your code less feral).

- **Docstrings**: Because future you will forget what that property was for.

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
- **CSRF Tokens**:
  - Always include CSRF tokens in test requests
  - Use `client.get('/')` to fetch CSRF token before POST requests
  - Validate CSRF tokens in all form submissions
- **Route Registration**:
  - Register admin routes before public routes
  - Use debug logging to verify route registration order
  - Test route accessibility after registration

## 7. Error Handling & Organization
- **Centralized Errors**: Single source of truth for messages, making your logs (and your sanity) that much better.
- **Graceful Fails**: If a package is missing, skip the test. Don’t throw the entire test suite off the cliff.  
- **Modular Code**: Minimal duplication, maximum reusability. Keep your code as neat as your desk (or neater, sir).

## Route Naming Conventions

1. **Blueprint Names**:
   - Use lowercase with underscores (e.g., `admin_stipend_bp`).

2. **Endpoint Names**:
   - Use lowercase with dots (e.g., `admin_stipend.create`).

3. **URL Prefixes**:
   - Use consistent prefixes for related routes (e.g., `/admin/stipends`).

## 8. use newest versions of all moduels and libraries
- **Up-to-date**: Keep your modules and libraries up-to-date to ensure you're using the latest features and security patches. Ensure requirements.txt reflects the latest versions of all dependencies.

## 9. About This Environment

- **Virtual Environment**:  
  You are currently running on a windows machine inside an activated venv with all dependencies from requirements.txt already installed.

- **TODO.txt**:  
  A file to keep track of tasks, ideas, or anything that needs to be addressed later. It's a simple text file where you can jot down notes, reminders, or to-dos. You can use it to capture ideas, brainstorm, or plan your work. It's a flexible tool that allows you to organize your thoughts and keep track of your tasks in a simple and accessible format. Periodically review and compress this file if it gets too big.

- **autocoder**:  
  You are running in a coding cycle that looks like this (plan and act accordingly, don't do too much in one go, you can always come back to it and continue next cycle):

  **Step 1: Identify & Plan**  
  - Read your project details (TODOs, conventions, validations).  
  - Decide what to tackle and how.  
  - Potentially run any step-specific console commands (like migrations) before moving on.

  **Step 2: Test & Debug**  
  - Run your tests to see what breaks.  
  - Fix those issues based on the test feedback.  
  - If you need extra console commands to help debug, run them here.

  **Step 3: Refine & Summarize**  
  - Do some final polishing (refactoring, reorganizing, etc.).  
  - Summarize the current state of the code so you know exactly where you stand.

  **Step 4: Optional Additional Checks**  
  - Perform housekeeping: extra tests, coverage checks, or final quality gates.  
  - If new issues pop up, fix them here. Run console commands if needed.

  **Step 5: Final Documentation Updates**  
  - Update TODO.txt or any project docs with what you changed, how you fixed it, and why.  
  - Then either wrap up or reset to start the next cycle.
