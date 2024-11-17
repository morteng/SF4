# Testing Specification for the Stipend Discovery Website

This testing specification outlines the requirements and guidelines for implementing tests in the **Stipend Discovery Website** project. The goal is to ensure code reliability and maintain high quality through comprehensive testing.

---

## Overview

- **Testing Framework**: `pytest`
- **Coverage Tool**: `pytest-cov`
- **Test Types**:
  - Unit Tests
  - Integration Tests
  - End-to-End Tests
- **Organization**: Tests should mirror the application's structure within the `tests/` directory.

---

## Requirements

### 1. Testing Framework and Tools

- Use `pytest` for writing and running tests.
- Use `pytest-cov` to measure test coverage and generate reports.
- Ensure all testing dependencies are listed in `requirements.txt`.

### 2. Test Coverage

- Aim for high test coverage (minimum **80%**).
- Include tests for all critical paths:
  - Models
  - Views (routes)
  - Services
  - Utilities
- Measure coverage using `pytest-cov` and generate reports on each test run.

### 3. Test Organization

- **Directory Structure**:

  ```
  tests/
    conftest.py
    test_models/
      test_user.py
      test_stipend.py
      test_organization.py
      test_tag.py
    test_routes/
      test_user_routes.py
      test_admin_routes.py
      test_bot_routes.py
    test_services/
      test_bot_service.py
      test_tag_service.py
      test_notification_service.py
  ```

- **Naming Conventions**:
  - Test files: `test_*.py`
  - Test classes: `Test*`
  - Test functions: `test_*`

### 4. Types of Tests

#### Unit Tests

- **Purpose**: Test individual functions or methods in isolation.
- **Scope**: Models, services, utility functions.
- **Example**: Testing the `set_password` method in the `User` model.

#### Integration Tests

- **Purpose**: Test the interaction between different components.
- **Scope**: Database operations, API endpoints, services interacting with models.
- **Example**: Testing that creating a new stipend via the admin interface correctly updates the database.

#### End-to-End Tests

- **Purpose**: Simulate user behavior across the entire application.
- **Scope**: User workflows, form submissions, navigation.
- **Example**: Testing the stipend search functionality from the user's perspective.

### 5. Test Data and Fixtures

- Use **fixtures** in `conftest.py` for setting up common test data and resources.
- **Database Fixtures**:
  - Use an in-memory SQLite database for testing to ensure isolation.
  - Set up and tear down the database before and after each test or test session.
- **Client Fixture**:
  - Use Flask's `test_client()` for simulating HTTP requests in route tests.

### 6. Testing Configuration

- **Configuration Files**:
  - Create `pytest.ini` for pytest configurations.
- **Testing Settings**:
  - Use a separate testing configuration (`TestingConfig`) that specifies testing settings, such as an in-memory database.
  - Disable unnecessary features during testing (e.g., CSRF protection).

### 7. Running Tests and Generating Reports

- **Run all tests**: `pytest`
- **Run specific tests**: `pytest tests/test_models/test_user.py`
- **Generate coverage report**: `pytest --cov=app --cov-report=html`
  - View the report by opening `htmlcov/index.html` in a browser.

---

## Guidelines for Writing Tests

1. **Isolation**: Ensure tests do not depend on each other.
2. **Clarity**: Use descriptive names for test functions and variables.
3. **Assertions**: Write clear assertions to validate expected outcomes.
4. **Error Handling**: Test how the application handles invalid inputs and exceptions.
5. **Edge Cases**: Include tests for edge cases and boundary conditions.
6. **Documentation**: Add docstrings or comments to explain complex tests.

---

## Example Test Cases

### Unit Test Example

```python
# tests/test_models/test_user.py

def test_set_password():
    from app.models.user import User
    user = User(username='testuser')
    user.set_password('testpassword')
    assert user.password_hash is not None
    assert user.check_password('testpassword') is True
```

### Integration Test Example

```python
# tests/test_routes/test_admin_routes.py

def test_admin_create_stipend(client, session):
    # Log in as admin
    response = client.post('/admin/login', data={
        'username': 'admin_user',
        'password': 'secure_password'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Dashboard' in response.data

    # Create a new stipend
    response = client.post('/admin/stipends/create', data={
        'name': 'Sample Stipend',
        'summary': 'Sample summary',
        'description': 'Sample description',
        # Additional fields...
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Sample Stipend' in response.data

    # Verify in database
    from app.models.stipend import Stipend
    stipend = session.query(Stipend).filter_by(name='Sample Stipend').first()
    assert stipend is not None
```

### End-to-End Test Example

```python
# tests/test_routes/test_user_routes.py

def test_stipend_search(client, session):
    # Add test data to the database
    from app.models.stipend import Stipend
    stipend = Stipend(name='Test Stipend', summary='Test Summary')
    session.add(stipend)
    session.commit()

    # Simulate user searching for the stipend
    response = client.get('/search?query=Test+Stipend')
    assert response.status_code == 200
    assert b'Test Stipend' in response.data
```

---

## Testing Environment Configuration

- **Testing Configuration Class** in `config.py`:

  ```python
  class TestingConfig(Config):
      TESTING = True
      SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
      WTF_CSRF_ENABLED = False  # Disable CSRF for testing
  ```

- **App Factory** in `app/__init__.py`:

  ```python
  def create_app(config_name='default'):
      # Load configuration
      if config_name == 'testing':
          app.config.from_object('config.TestingConfig')
      else:
          app.config.from_object('config.Config')
      # Initialize extensions and blueprints
      return app
  ```

- **Fixtures** in `tests/conftest.py`:

  ```python
  @pytest.fixture(scope='session')
  def app():
      app = create_app('testing')
      return app

  @pytest.fixture(scope='session')
  def db(app):
      with app.app_context():
          db.create_all()
          yield db
          db.drop_all()

  @pytest.fixture(scope='function')
  def session(db):
      connection = db.engine.connect()
      transaction = connection.begin()
      options = dict(bind=connection)
      session = db.create_scoped_session(options=options)
      yield session
      transaction.rollback()
      connection.close()
      session.remove()

  @pytest.fixture(scope='function')
  def client(app):
      with app.test_client() as client:
          yield client
  ```

---

## Additional Considerations

- **Mocking**: Use mocking for external dependencies (e.g., APIs) to isolate tests.
- **Continuous Testing**: Run tests frequently during development to catch issues early.
- **Performance**: Keep tests efficient to avoid slowing down development workflow.
- **Error Reporting**: If tests fail, provide clear error messages to facilitate debugging.

---

## Responsibilities

- **Developers** are responsible for:
  - Writing tests for new features and bug fixes.
  - Ensuring all tests pass before merging code.
  - Maintaining existing tests when making changes.

---

By following this testing specification, the project will maintain a high level of code quality, reliability, and facilitate easier maintenance and scalability.