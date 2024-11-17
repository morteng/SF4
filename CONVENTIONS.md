# conventions.md

## Coding Conventions

This document outlines the coding conventions and best practices to follow when working on the **Stipend Discovery Website** project.

---

### General Principles

- **Modularity**: Keep code files short, modular, and well-documented.
- **PEP 8 Compliance**: Adhere to Python's PEP 8 style guidelines for consistency.
- **Separation of Concerns**: Maintain clear separation between models, views, controllers, and services.
- **Readability**: Write clear and understandable code with meaningful variable and function names.
- **Documentation**: Use docstrings and comments to explain complex logic and provide context.

### Project Structure

- **Routes**: Split routes into separate files according to functionality.
  - `user_routes.py`: User-facing routes.
  - `admin_routes.py`: Admin CRUD operations.
  - `bot_routes.py`: Bot management and monitoring.
- **Models**: Organize models into separate files per entity.
  - `stipend.py`, `organization.py`, `tag.py`, etc.
- **Services**: Encapsulate business logic in services.
  - `bot_service.py`, `tag_service.py`, etc.
- **Tests**: Mirror the application structure in the `tests/` directory.
  - `test_routes/`, `test_models/`, `test_services/`.

### Coding Practices

- **Small Commits**: Make small, frequent commits with clear and descriptive messages.
- **Test-Driven Development**: Write tests before implementing functionality.
- **Functionality Scope**: Focus on one piece of functionality at a time.
- **Error Handling**: Implement robust error handling and logging.
- **Version Control**: Maintain a clean Git history with meaningful commit messages.

### Testing Conventions

- **Unit Tests**: Write unit tests for individual functions and modules.
- **Integration Tests**: Ensure different components work together as expected.
- **End-to-End Tests**: Simulate user interactions to validate system behavior.
- **Test Coverage**: Use `pytest-cov` to aim for high test coverage.
- **Continuous Testing**: Run tests frequently to catch issues early.

### Aider-Specific Guidelines

- **Interactive Sessions**: Use Aider's interactive capabilities to refine code iteratively.
- **Code Reviews**: Utilize Aider to assist in code reviews and highlight potential issues.
- **Documentation Updates**: Keep documentation up-to-date when code changes are made.
- **Consistency**: Ensure that any code generated or modified with Aider adheres to the project's coding conventions.

---

## Environment and Configuration

### Environment Variables

- **Secure Loading**: Load environment variables from the `.env` file using a secure method.
- **No Hard-Coding**: Do not hard-code sensitive information in the codebase.
- **Version Control**: Ensure that the `.env` file is excluded from version control (`.gitignore`).

### Error Logging and Monitoring

- **Logging Framework**: Use Python's `logging` module for logging.
- **Log Levels**: Keep log statements meaningful and at appropriate levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`).
- **Log Rotation**: Implement log rotation to prevent log files from becoming too large.

### Security Practices

- **Authentication Checks**: Secure admin routes with proper authentication.
- **Input Validation**: Validate and sanitize all user inputs.
- **Dependency Management**: Keep dependencies updated to mitigate security vulnerabilities.

---

## Collaboration Guidelines

### Branching Strategy

- **Feature Branches**: Use feature branches for new functionality.
- **Naming Convention**: Use descriptive names for branches (e.g., `feature/add-login`, `bugfix/fix-routing`).

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

## Additional Notes

### Frontend Practices

- **HTMX Usage**: Utilize HTMX for dynamic frontend interactions wherever applicable.
- **Local Storage**: Use local storage to persist user preferences on the frontend.

### Database Migrations

- **Alembic**: Use Alembic for database schema changes and maintain migration scripts.
- **Version Control**: Ensure migration scripts are included in version control.

### Performance Optimization

- **Query Optimization**: Optimize database queries for efficiency.
- **Indexing**: Use indexing on frequently queried fields.
- **Caching**: Implement caching strategies if necessary.

