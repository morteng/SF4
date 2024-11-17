# Environment Configuration Specification for the Stipend Discovery Website

## Requirements

### 1. Environment Variables Management

- **Environment Variables File**:
  - Use a `.env` file located in the project's root directory to store environment variables.
  - Ensure the `.env` file is included in the `.gitignore` file to prevent it from being committed to version control.

- **Contents of `.env`**:
  - The `.env` file should contain the following variables:

    ```env
    SECRET_KEY=your_secret_key_here
    DATABASE_URL=sqlite:///site.db
    ADMIN_USERNAME=admin_user
    ADMIN_PASSWORD=secure_password
    ADMIN_EMAIL=admin@example.com
    ```

  - **Descriptions**:
    - `SECRET_KEY`: Used for Flask session management and CSRF protection.
    - `DATABASE_URL`: Database connection string.
    - `ADMIN_USERNAME`: Default admin username.
    - `ADMIN_PASSWORD`: Default admin password.
    - `ADMIN_EMAIL`: Default admin email address.

### 2. Loading Environment Variables

- **Library**: Use `python-dotenv` to load environment variables from the `.env` file.
- **Application Initialization**:
  - Modify the application's initialization code to load the `.env` file before accessing environment variables.
  - Example:

    ```python
    from dotenv import load_dotenv
    import os

    def create_app(config_name=None):
        load_dotenv()
        app = Flask(__name__)
        # Configuration and initialization...
        return app
    ```

### 3. Application Configuration

- **Configuration Classes**:
  - Update configuration classes (`Config`, `DevelopmentConfig`, `TestingConfig`, `ProductionConfig`) to retrieve settings from environment variables using `os.environ.get()`.
  - Provide default fallback values where appropriate.

- **Configuration Selection**:
  - The application should select the appropriate configuration class based on the `FLASK_CONFIG` environment variable.
  - Example:

    ```python
    config_name = os.environ.get('FLASK_CONFIG', 'default')
    ```

### 4. Default Admin User Setup

- **User Model**:
  - The `User` model should include fields:
    - `username`
    - `password_hash`
    - `email`
    - `is_admin`
    - Timestamps: `created_at`, `updated_at`

- **Password Handling**:
  - Use `werkzeug.security` for password hashing (`generate_password_hash`, `check_password_hash`).

- **Admin User Initialization**:
  - Implement a function to create the default admin user if it doesn't already exist, using credentials from environment variables.
  - Example:

    ```python
    def init_admin_user():
        username = os.environ.get('ADMIN_USERNAME')
        password = os.environ.get('ADMIN_PASSWORD')
        email = os.environ.get('ADMIN_EMAIL')
        # Check and create admin user...
    ```

- **Application Startup**:
  - Call the admin initialization function during application startup, after database initialization.
  - Ensure this operation occurs within the application context.

### 5. Security Considerations

- **Sensitive Data Protection**:
  - Do not hard-code sensitive information in the codebase.
  - Ensure the `.env` file is excluded from version control.

- **Environment Variables Handling**:
  - Provide clear error messages if essential environment variables are missing.
  - Prevent the application from starting if critical configurations are not set.

- **Password Security**:
  - Store passwords securely using salted hashes.
  - Do not store plaintext passwords.

### 6. Testing Environment Variable Loading

- **Testing Access**:
  - Write tests to ensure environment variables are loaded correctly and accessible within the application.

- **Admin User Creation Test**:
  - Implement tests to verify that the admin user is created correctly during application initialization.

### 7. Documentation

- **Setup Instructions**:
  - Include instructions in the `README.md` or setup documentation on:
    - Creating the `.env` file based on a template.
    - Keeping the `.env` file out of version control.
    - Setting environment variables for different environments (development, testing, production).

---

## Guidelines

- **Consistency**:
  - Use environment variables for all configurations that may change between environments.

- **Error Handling**:
  - Implement checks and informative messages for missing environment variables.

- **Avoid Hardcoding**:
  - Do not hard-code default credentials or sensitive information in the codebase.

- **Security Best Practices**:
  - Use secure password hashing methods.
  - Ensure that secret keys and passwords are not exposed.

- **Testing**:
  - Include tests to verify environment variable loading and admin user initialization.

### 8. startup

- **Application files and configs**:
  - startup.py - A script to init db, do any migrations, update dbs, and create the admin user. Then run tests, abort if tests fail. Then run the app.
  - config.py - A config file that contains the configuration classes for the app.
  - tests/conftest.py - A file that contains the fixtures for the tests.