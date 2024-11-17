# Project Specification: Stipend Discovery Website

## Project Overview

The **Stipend Discovery Website** is a Flask-based application designed to help users explore and filter stipends dynamically. The platform utilizes HTMX for real-time interaction and provides a mobile-first, responsive design. An admin interface allows for secure CRUD operations on stipends, tags, and organizations. Automated bots handle data scraping, tagging, validation, and updates to streamline operations.

---

## Key Features

- **User-Facing Discovery Tool**: Interactive tag-based filtering interface using HTMX for real-time updates.
- **Admin CRUD Interface**: Secure, authenticated interface for managing stipends, tags, organizations, and bot operations.
- **Automated Bots**: Bots for data scraping, tagging (TagBot), updating (UpdateBot), and validation (ReviewBot).
- **Dynamic Content Updates**: Real-time content updates using HTMX/AJAX for seamless user interaction.
- **Quality Assurance on Startup**: The system runs test coverage reports on startup, ensuring code health and reliability.

---

## Technical Stack

### Backend

- **Framework**: Flask (Python)
- **Database**: SQLite (loaded in-memory for performance)
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
- **Coverage**: `pytest-cov` with auto-generated reports on startup.

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

4. **Bots**
   - **Fields**: `bot_id` (PK), `name`, `description`, `status`, `last_run`, `error_log`.

5. **Notifications**
   - **Fields**: `id` (PK), `message`, `type` (info, warning, error), `read_status` (Boolean), `created_at`.

6. **Users**
   - **Fields**: `id` (PK), `username`, `password_hash`, `created_at`, `updated_at`, `is_admin` (Boolean).

### Relationships

- **Many-to-Many**:
  - `Stipends` ↔ `Tags`
  - `Stipends` ↔ `Organizations`

---

## System Components

### Database Initialization

- **Script**: Instantiate and populate the database with default values.
- **Relationships**: Set up many-to-many relationships between stipends, tags, and organizations.

### User-Facing Pages

- **Homepage**: Displays popular stipends and tag-based filters.
- **Stipend Search**: HTMX-powered tag and keyword filtering with real-time updates.
- **Stipend Details Page**: Full stipend details, eligibility, application procedure, and organization links.

### Admin Section (CRUD with Authentication)

- **Login System**: Basic authentication for the admin portal.
- **CRUD Pages**: Manage stipends, tags, organizations, and bots.
- **Bot Management**: Dashboard for monitoring bot status and scheduling operations.
- **Notifications**: Real-time admin notifications for bot updates, errors, and flagged stipend entries.

### Automated Bot System

- **TagBot**: Tags stipends based on content.
- **UpdateBot**: Refreshes stipend data, flags invalid URLs, manages stale information.
- **ReviewBot**: Performs sanity checks, flags suspicious items, notifies admin for review.
- **Scheduler**: Admin-controlled bot scheduler with logging for status and error handling.

---

## Code Quality and Testing Practices

### Best Practices and Modularity

- **PEP 8 Compliance**: Adhere to Python's PEP 8 style guidelines.
- **Separation of Concerns**: Clear division between models, views, controllers, and services.
- **Modularity**: Keep code files short, modular, and well-documented.

### Testing Framework

- **Unit Tests**: Write tests for each function and module using `pytest`.
- **Integration Tests**: Ensure components work together as expected.
- **End-to-End Tests**: Simulate user interactions to validate system behavior.
- **Test Coverage**: Use `pytest-cov` to aim for high test coverage.

### Coverage Reports on Startup

- **Automated Testing**: `pytest-cov` generates test coverage reports at each startup.
- **Error Alerts**: Logs and notifications alert the admin if tests fail or coverage drops.

### Error Handling and Logging

- **Structured Logging**: Use Python’s logging module with structured logs.
- **Detailed Logs**: Capture bot failures, test errors, and system status for responsive debugging.

---

## Security Considerations

- **Authentication**: Secure login page with basic authentication for admins.
- **Data Integrity**: Bots flag entries for review instead of deletion to maintain data accuracy.
- **Rate Limiting**: Conservative scraping approach to prevent server strain and IP blocks.

---

## System Flow

1. **Data Acquisition and Management**: Bots populate, tag, and verify stipend data.
2. **User Interaction**: Users engage with an interactive interface using HTMX and local storage for preferences.
3. **Admin Monitoring**: Admins manage data, schedule bot operations, and receive real-time alerts.

---

## Coding Practices

1. **Small Commits**: Make small, frequent commits with clear messages.
2. **Test-Driven Development**: Write tests before implementing functionality.
3. **Code Style**: Follow PEP 8 standards and best practices.
4. **Version Control**: Use meaningful commit messages and maintain a clean Git history.
5. **Documentation**: Keep code well-documented with docstrings and comments.

---

## Testing Practices

1. **Unit Tests**: Test individual functions and modules.
2. **Integration Tests**: Test interactions between different components.
3. **End-to-End Tests**: Validate the system from a user's perspective.
4. **Test Coverage**: Aim for high coverage to ensure all code paths are tested.

---

## Environment Variables

The application uses a `.env` file to manage environment variables securely. Ensure the application loads these variables from the `.env` file.

### `.env` Contents

```env
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///site.db
ADMIN_USERNAME=admin_user
ADMIN_PASSWORD=secure_password
ADMIN_EMAIL=admin@example.com
```

---

## Notes to Read and Follow

- **Route Organization**: Split routes into separate files according to functionality:
  - `user_routes.py` for user-facing routes.
  - `admin_routes.py` for admin CRUD operations.
  - `bot_routes.py` for bot management.
- **Testing Organization**: Split tests into separate files mirroring the application structure.
- **Code Organization**: Keep code files short, modular, and well-documented.
- **Local Storage**: Use local storage to persist user preferences on the frontend.
- **HTMX Usage**: Utilize HTMX for dynamic interactions wherever possible.

---

## Folder Structure

```plaintext
app/
  __init__.py
  routes/
    __init__.py
    user_routes.py
    admin_routes.py
    bot_routes.py
  models/
    __init__.py
    stipend.py
    organization.py
    tag.py
    bot.py
    notification.py
    user.py
  templates/
    base.html
    user/
      index.html
      stipend_detail.html
    admin/
      dashboard.html
      stipend_form.html
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
    test_routes/
      test_user_routes.py
      test_admin_routes.py
      test_bot_routes.py
    test_models/
      test_stipend_model.py
      test_organization_model.py
    test_services/
      test_bot_service.py
      test_tag_service.py
    conftest.py
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

---

## Conclusion

This document provides a comprehensive guide for developing the backend of the **Stipend Discovery Website**. It focuses on the essential components needed to get the application operational, including database design, system architecture, coding standards, and testing strategies. Frontend development will be addressed after the backend and bots are fully functional.
