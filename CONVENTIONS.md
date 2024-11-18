# Project Specification: Stipend Discovery Website

## Table of Contents

1. [Introduction](#introduction)
2. [Project Overview](#project-overview)
3. [Key Features](#key-features)
4. [Technical Stack](#technical-stack)
5. [Database Schema](#database-schema)
6. [System Components](#system-components)
7. [Coding Conventions](#coding-conventions)
8. [Coding Practices](#coding-practices)
9. [Testing Specification](#testing-specification)
10. [Environment and Configuration](#environment-and-configuration)
11. [Security Considerations](#security-considerations)
12. [System Flow](#system-flow)
13. [Collaboration Guidelines](#collaboration-guidelines)
14. [Documentation](#documentation)
15. [Folder Structure](#folder-structure)
16. [Additional Components](#additional-components)
17. [Conclusion](#conclusion)

---

## Introduction

This document provides a comprehensive guide for developing the **Stipend Discovery Website**, consolidating all relevant information into a single resource. It outlines the project's specifications, coding conventions, system architecture, testing strategies, and more. The goal is to ensure that all team members have a clear understanding of the project's requirements and standards.

---

## Project Overview

The **Stipend Discovery Website** is a Flask-based application designed to help users explore and filter stipends dynamically. The platform utilizes HTMX for real-time interaction and provides a mobile-first, responsive design. An admin interface allows for secure CRUD operations on stipends, tags, organizations, and users. Automated bots handle data scraping, tagging, validation, and updates to streamline operations.

---

## Key Features

- **User-Facing Discovery Tool**: Interactive tag-based filtering interface using HTMX for real-time updates.
- **Admin CRUD Interface**: Secure, authenticated interface for managing stipends, tags, organizations, users, and bot operations.
- **Automated Bots**: Bots for data scraping, tagging (TagBot), updating (UpdateBot), and validation (ReviewBot).
- **Dynamic Content Updates**: Real-time content updates using HTMX/AJAX for seamless user interaction.
- **Quality Assurance on Startup**: The system runs test coverage reports on startup, ensuring code health and reliability.

---

## Technical Stack

### Backend

- **Framework**: Flask (Python)
- **Database**: SQLite for development; consider PostgreSQL for production
- **Interaction**: HTMX for real-time updates
- **Bots**:
  - **TagBot**: Automatically tags stipends based on content.
  - **UpdateBot**: Updates stipend information and flags outdated entries.
  - **ReviewBot**: Flags invalid or suspicious stipend entries for admin review.

### Frontend

- **HTML**: Base templates with modular extensions.
- **CSS**: Mobile-first responsive design.
- **JavaScript**: HTMX for dynamic user interaction.

### Testing

- **Framework**: `pytest`
- **Coverage**: `pytest-cov` to measure test coverage and generate reports.
- **Test Types**:
  - Unit Tests
  - Integration Tests
  - End-to-End Tests

### Security

- **Authentication**: Basic authentication for admin interface.
- **Data Integrity**: Bots flag invalid data for admin review instead of deletion.
- **Scraping Policy**: Conservative rate limiting to avoid IP blocks.

---

## Database Schema

### Tables and Fields

1. **Stipends**
   - **Fields**: `id` (PK), `name`, `summary`, `description`, `homepage_url`, `application_procedure`, `eligibility_criteria`, `application_deadline`, `open_for_applications` (Boolean), `created_at`, `updated_at`.
   - **Relationships**: Many-to-many with `Tags`, many-to-many with `Organizations`.

2. **Organizations**
   - **Fields**: `id` (PK), `name`, `description`, `homepage_url`, `created_at`, `updated_at`.

3. **Tags**
   - **Fields**: `id` (PK), `name`, `category`.
   - **Relationships**: Many-to-many with `Stipends`.

4. **Users**
   - **Fields**: `id` (PK), `username`, `password_hash`, `email`, `is_admin` (Boolean), `created_at`, `updated_at`.

5. **Bots**
   - **Fields**: `id` (PK), `name`, `description`, `status`, `last_run`, `error_log`.

6. **Notifications**
   - **Fields**: `id` (PK), `message`, `type` (info, warning, error), `read_status` (Boolean), `created_at`.

### Relationships

- **Many-to-Many**:
  - `Stipends` ↔ `Tags`
  - `Stipends` ↔ `Organizations`

---

## System Components

### Database Initialization

- **Script**: A `startup.py` script to initialize the database, perform migrations, and create the default admin user.
- **Relationships**: Set up many-to-many relationships between stipends, tags, and organizations.

### User-Facing Pages

- **Homepage**: Displays popular stipends and tag-based filters.
- **Stipend Search**: HTMX-powered tag and keyword filtering with real-time updates.
- **Stipend Details Page**: Full stipend details, eligibility, application procedure, and organization links.

### Admin Section (CRUD with Authentication)

- **Login System**: Basic authentication for the admin portal.
- **CRUD Pages**: Manage stipends, tags, organizations, users, and bots.
  - **Routes**: Split into separate files for better modularity:
    - `app/routes/admin/stipend_routes.py`
    - `app/routes/admin/tag_routes.py`
    - `app/routes/admin/organization_routes.py`
    - `app/routes/admin/user_routes.py`
    - `app/routes/admin/bot_routes.py`
- **Bot Management**: Dashboard for monitoring bot status and scheduling operations.
- **Notifications**: Real-time admin notifications for bot updates, errors, and flagged stipend entries.

### Automated Bot System

- **TagBot**: Tags stipends based on content.
- **UpdateBot**: Refreshes stipend data, flags invalid URLs, manages stale information.
- **ReviewBot**: Performs sanity checks, flags suspicious items, notifies admin for review.
- **Scheduler**: Admin-controlled bot scheduler with logging for status and error handling.

---

## Coding Conventions

### General Principles

- **Modularity**: Keep code files short, modular, and well-documented.
- **PEP 8 Compliance**: Adhere to Python's PEP 8 style guidelines for consistency.
- **Separation of Concerns**: Maintain clear separation between models, views, controllers, and services.
- **Readability**: Write clear and understandable code with meaningful variable and function names.
- **Documentation**: Use docstrings and comments to explain complex logic and provide context.

### Project Structure

- **Routes**: Split routes into separate files according to functionality.
  - `user_routes.py`: User-facing routes.
  - **Admin Routes**: Located under `app/routes/admin/` directory.
    - `bot_routes.py`: Manage bot configurations and monitoring.
    - `organization_routes.py`: Manage organizations and their details.
    - `stipend_routes.py`: Manage stipends and their details.
    - `tag_routes.py`: Manage tags and categories.
    - `user_routes.py`: Manage user accounts and permissions.
- **Static Files**: Organize static files (CSS, JavaScript, images) into separate directories.
  - `static/css/`, `static/js/`, `static/images/`.
- **Templates**: Keep templates clean and modular, using template inheritance for consistency.
- **Models**: Organize models into separate files per entity.
  - `stipend.py`, `organization.py`, `tag.py`, `user.py`, etc.
- **Services**: Encapsulate business logic in services.
  - `bot_service.py`, `tag_service.py`, etc.
- **Tests**: Mirror the application structure in the `tests/` directory.
  - `test_routes/`, `test_models/`, `test_services/`.

---

## Coding Practices

1. **Small Commits**: Make small, frequent commits with clear and descriptive messages.
2. **Test-Driven Development**: Write tests before implementing functionality.
3. **Functionality Scope**: Focus on one piece of functionality at a time.
4. **Error Handling**: Implement robust error handling and logging.
5. **Version Control**: Maintain a clean Git history with meaningful commit messages.
6. **Code Reviews**: Submit pull requests for code reviews before merging into the main branch.

---

## Testing Specification

This testing specification outlines the requirements and guidelines for implementing tests in the **Stipend Discovery Website** project. The goal is to ensure code reliability and maintain high quality through comprehensive testing.

### Overview

- **Testing Framework**: `pytest`
- **Coverage Tool**: `pytest-cov`
- **Test Types**:
  - Unit Tests
  - Integration Tests
  - End-to-End Tests
- **Organization**: Tests should mirror the application's structure within the `tests/` directory.

### Requirements

#### 1. Testing Framework and Tools

- Use `pytest` for writing and running tests.
- Use `pytest-cov` to measure test coverage and generate reports.
- Ensure all testing dependencies are listed in `requirements.txt`.

#### 2. Test Coverage

- **Goal**: Aim for high test coverage (minimum **80%**).
- **Scope**: Include tests for all critical paths:
  - Models
  - Views (routes)
  - Services
  - Utilities
- **Coverage Reports**: Measure coverage using `pytest-cov` and generate reports on each test run.

#### 3. Test Organization

- **Directory Structure**:

  ```plaintext
  tests/
    conftest.py
    test_models/
      test_user.py
      test_stipend.py
      test_organization.py
      test_tag.py
    test_routes/
      test_user_routes.py
      admin/
        test_stipend_routes.py
        test_tag_routes.py
        test_organization_routes.py
        test_user_routes.py
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

#### 4. Types of Tests

##### Unit Tests

- **Purpose**: Test individual functions or methods in isolation.
- **Scope**: Models, services, utility functions.
- **Example**: Testing the `set_password` method in the `User` model.

##### Integration Tests

- **Purpose**: Test the interaction between different components.
- **Scope**: Database operations, API endpoints, services interacting with models.
- **Example**: Testing that creating a new stipend via the admin interface correctly updates the database.

##### End-to-End Tests

- **Purpose**: Simulate user behavior across the entire application.
- **Scope**: User workflows, form submissions, navigation.
- **Example**: Testing the stipend search functionality from the user's perspective.

#### 5. Test Data and Fixtures

- Use **fixtures** in `conftest.py` for setting up common test data and resources.
- **Database Fixtures**:
  - Use an in-memory SQLite database for testing to ensure isolation.
  - Set up and tear down the database before and after each test or test session.
- **Client Fixture**:
  - Use Flask's `test_client()` for simulating HTTP requests in route tests.

#### 6. Testing Configuration

- **Configuration Files**:
  - Create `pytest.ini` for pytest configurations.
- **Testing Settings**:
  - Use a separate testing configuration (`TestingConfig`) that specifies testing settings, such as an in-memory database.
  - Disable unnecessary features during testing (e.g., CSRF protection).

#### 7. Running Tests and Generating Reports

- **Run all tests**: `pytest`
- **Run specific tests**: `pytest tests/test_models/test_user.py`
- **Generate coverage report**: `pytest --cov=app --cov-report=html`
  - View the report by opening `htmlcov/index.html` in a browser.

### Guidelines for Writing Tests

1. **Isolation**: Ensure tests do not depend on each other.
2. **Clarity**: Use descriptive names for test functions and variables.
3. **Assertions**: Write clear assertions to validate expected outcomes.
4. **Error Handling**: Test how the application handles invalid inputs and exceptions.
5. **Edge Cases**: Include tests for edge cases and boundary conditions.
6. **Documentation**: Add docstrings or comments to explain complex tests.

### Example Test Cases

#### Unit Test Example

```python
# tests/test_models/test_user.py

def test_set_password():
    from app.models.user import User
    user = User(username='testuser')
    user.set_password('testpassword')
    assert user.password_hash is not None
    assert user.check_password('testpassword') is True
```

#### Integration Test Example

```python
# tests/test_routes/admin/test_stipend_routes.py

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

#### End-to-End Test Example

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

### Testing Environment Configuration

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

### Additional Considerations

- **Mocking**: Use mocking for external dependencies (e.g., APIs) to isolate tests.
- **Continuous Testing**: Run tests frequently during development to catch issues early.
- **Performance**: Keep tests efficient to avoid slowing down development workflow.
- **Error Reporting**: If tests fail, provide clear error messages to facilitate debugging.

### Responsibilities

- **Developers** are responsible for:
  - Writing tests for new features and bug fixes.
  - Ensuring all tests pass before merging code.
  - Maintaining existing tests when making changes.

---

## Environment and Configuration

### Environment Variables Management

- **.env File**:
  - Located in the project's root directory.
  - Excluded from version control via `.gitignore`.

- **Contents of `.env`**:

  ```env
  SECRET_KEY=your_secret_key_here
  DATABASE_URL=sqlite:///site.db
  ADMIN_USERNAME=admin_user
  ADMIN_PASSWORD=secure_password
  ADMIN_EMAIL=admin@example.com
  FLASK_CONFIG=development
  ```

- **Descriptions**:
  - `SECRET_KEY`: Used for Flask session management and CSRF protection.
  - `DATABASE_URL`: Database connection string.
  - `ADMIN_USERNAME`: Default admin username.
  - `ADMIN_PASSWORD`: Default admin password.
  - `ADMIN_EMAIL`: Default admin email address.
  - `FLASK_CONFIG`: Specifies the Flask configuration to use.

### Loading Environment Variables

- **Library**: Use `python-dotenv` to load environment variables from the `.env` file.
- **Application Initialization**:

  ```python
  from dotenv import load_dotenv
  import os

  def create_app(config_name=None):
      load_dotenv()
      app = Flask(__name__)
      # Configuration and initialization...
      return app
  ```

### Application Configuration

- **Configuration Classes**: (`Config`, `DevelopmentConfig`, `TestingConfig`, `ProductionConfig`)
  - Retrieve settings from environment variables using `os.environ.get()`.
  - Provide default fallback values where appropriate.
- **Configuration Selection**:

  ```python
  config_name = os.environ.get('FLASK_CONFIG', 'default')
  ```

### Default Admin User Setup

- **User Model**:
  - Fields: `username`, `password_hash`, `email`, `is_admin`, `created_at`, `updated_at`.
- **Password Handling**:
  - Use `werkzeug.security` for password hashing (`generate_password_hash`, `check_password_hash`).
- **Admin User Initialization**:

  ```python
  def init_admin_user():
      username = os.environ.get('ADMIN_USERNAME')
      password = os.environ.get('ADMIN_PASSWORD')
      email = os.environ.get('ADMIN_EMAIL')
      # Check and create admin user...
  ```

- **Application Startup**:
  - Call the admin initialization function during application startup, after database initialization.

### Security Considerations

- **Sensitive Data Protection**:
  - Do not hard-code sensitive information in the codebase.
  - Ensure the `.env` file is excluded from version control.
- **Environment Variables Handling**:
  - Provide clear error messages if essential environment variables are missing.
  - Prevent the application from starting if critical configurations are not set.
- **Password Security**:
  - Store passwords securely using salted hashes.
  - Do not store plaintext passwords.

### Testing Environment Variable Loading

- **Testing Access**:
  - Write tests to ensure environment variables are loaded correctly and accessible within the application.
- **Admin User Creation Test**:
  - Implement tests to verify that the admin user is created correctly during application initialization.

### Documentation

- **Setup Instructions**:
  - Include instructions in the `README.md` on:
    - Creating the `.env` file based on a template.
    - Keeping the `.env` file out of version control.
    - Setting environment variables for different environments.

---

## Security Considerations

- **Authentication Checks**: Secure admin routes with proper authentication.
- **Input Validation**: Validate and sanitize all user inputs.
- **Dependency Management**: Keep dependencies updated to mitigate security vulnerabilities.
- **Rate Limiting**: Implement conservative scraping approaches to prevent server strain and IP blocks.
- **Data Integrity**: Bots flag entries for review instead of deletion to maintain data accuracy.
- **Error Logging and Monitoring**:
  - Use Python's `logging` module.
  - Implement log rotation to manage file sizes.

---

## System Flow

1. **Data Acquisition and Management**: Bots populate, tag, and verify stipend data.
2. **User Interaction**: Users engage with an interactive interface using HTMX and local storage for preferences.
3. **Admin Monitoring**: Admins manage data, schedule bot operations, and receive real-time alerts.

---

## Collaboration Guidelines

### Branching Strategy

- **Feature Branches**: Use feature branches for new functionality.
- **Naming Convention**: Use descriptive names (e.g., `feature/add-login`, `bugfix/fix-routing`).

### Pull Requests

- **Code Reviews**: Submit pull requests for code reviews before merging into the main branch.
- **Review Criteria**: Check for code quality, adherence to conventions, and potential issues.

### Commit Messages

- **Descriptive Messages**: Write clear and descriptive commit messages.
- **Small Commits**: Commit small, incremental changes to make reviews easier.

---

## Documentation

### README.md

- **Project Overview**: Keep the README updated with project descriptions and setup instructions.
- **Dependencies**: List all required dependencies and how to install them.
- **Setup Instructions**: Provide clear steps to set up the development environment.

### Code Documentation

- **Docstrings**: Use docstrings for modules, classes, and functions to explain their purpose.
- **Inline Comments**: Add comments to explain complex logic or decisions.

### Contributions

- **Non-Obvious Decisions**: Document any non-obvious decisions or workarounds in code comments or additional documentation.

---

## Folder Structure

```plaintext
app/
  __init__.py
  routes/
    __init__.py
    user_routes.py
    admin/
      __init__.py
      bot_routes.py
      organization_routes.py
      stipend_routes.py
      tag_routes.py
      user_routes.py
  models/
    __init__.py
    stipend.py
    organization.py
    tag.py
    user.py
    bot.py
    notification.py
  templates/
    base.html
    user/
      index.html
      stipend_detail.html
    admin/
      dashboard.html
      stipend_form.html
      tag_form.html
      organization_form.html
      user_form.html
      bot_dashboard.html
    errors/
      404.html
      500.html
  static/
    css/
      main.css
    js/
      main.js
    images/
  forms/
    __init__.py
    user_forms.py
    admin_forms.py
  services/
    __init__.py
    bot_service.py
    tag_service.py
    notification_service.py
  tests/
    conftest.py
    test_models/
      test_user.py
      test_stipend.py
      test_organization.py
      test_tag.py
    test_routes/
      test_user_routes.py
      admin/
        test_stipend_routes.py
        test_tag_routes.py
        test_organization_routes.py
        test_user_routes.py
        test_bot_routes.py
    test_services/
      test_bot_service.py
      test_tag_service.py
      test_notification_service.py
  config.py
  db.py
bots/
  tag_bot.py
  update_bot.py
  review_bot.py
instance/
  site.db
  config.env
migrations/
.env
.gitignore
README.md
requirements.txt
startup.py
wsgi.py
```

---

## Additional Components

### Error Logging and Monitoring

- **Logging Framework**: Use Python's `logging` module.
- **Log Management**:
  - **Location**: Store logs locally; consider cloud storage for backups.
  - **Rotation**: Implement log rotation to manage file sizes.

### Deployment Considerations

- **Environment**: Prepare for deployment on platforms like Render or Docker.
- **Environment Variables**: Securely manage via `.env` and deployment platform settings.
- **Database**: Use SQLite for development; consider PostgreSQL for production environments.

### Documentation and Versioning

- **Versioning**: Adopt semantic versioning for releases.
- **Developer Documentation**: Include setup instructions and project overview in `README.md`.
- **API Documentation**: Document any internal APIs used by bots or services.

### Data Backup and Recovery

- **Database Backups**:
  - **Frequency**: Schedule regular backups.
  - **Storage**: Securely store backups off-site or in the cloud.
- **Recovery Plan**: Provide scripts and documentation for restoring data.

### Performance Optimization

- **Database**:
  - **Indexing**: Index columns used in filtering and searching.
  - **Query Optimization**: Optimize database queries for efficiency.
- **Caching**: Implement caching strategies if necessary.
- **Frontend**:
  - **Minification**: Use minified assets to reduce load times.
  - **Lazy Loading**: Load resources as needed to improve performance.

### Frontend Practices

- **HTMX Usage**: Utilize HTMX for dynamic frontend interactions wherever applicable.
- **Local Storage**: Use local storage to persist user preferences on the frontend.
- **Responsive Design**: Ensure the frontend is mobile-first and responsive across devices.

### Database Migrations

- **Alembic**: Use Alembic for database schema changes and maintain migration scripts.
- **Version Control**: Ensure migration scripts are included in version control.

---

## Conclusion

This master document provides a comprehensive guide for developing the **Stipend Discovery Website**. It consolidates all relevant information, including project specifications, coding conventions, system architecture, testing strategies, and more. The focus is on building a robust backend with automated bots and a secure admin interface before addressing frontend development in detail. By adhering to the guidelines and standards outlined, the development team can ensure a high-quality, maintainable, and scalable application.

---

*Note: This document reflects the updated route organization, splitting the admin routes into several files under `app/routes/admin/`, and includes the detailed testing specification as per the latest updates.*