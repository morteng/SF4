# Project Specification: Stipend Discovery Website

## Introduction

This document provides a comprehensive guide for developing the **Stipend Discovery Website**. It consolidates project requirements, coding conventions, architecture, testing, and more. The goal is to ensure a crystal-clear blueprint for all team members.

---

## Project Overview

The **Stipend Discovery Website** is a Flask-based web application that helps users discover and filter stipends in real-time. It employs HTMX for dynamic interactions and offers a mobile-first, responsive design. The admin interface supports secure CRUD operations on stipends, tags, organizations, and users. Bots handle scraping, tagging, updates, and validation, streamlining data maintenance.

---

## Key Features

- **User-Facing Discovery**: Filter stipends by tags in real time using HTMX.  
- **Admin Interface**: Secure admin portal for CRUD operations on stipends, tags, organizations, users, and bot configuration.  
- **Automated Bots**: Handles scraping, tagging, data updates, and validation.  
- **Dynamic Content Updates**: Seamless, AJAX-like interactions without full-page reloads.  
- **Startup Quality Checks**: Automated tests run on startup to ensure code health.

---

## Technical Stack

**Backend**:  
- Flask (Python)  
- SQLite (dev) / PostgreSQL (prod)  
- Alembic for migrations  
- HTMX for dynamic interaction

**Bots**:  
- **TagBot**: Auto-tags stipends  
- **UpdateBot**: Updates and flags stale entries  
- **ReviewBot**: Flags suspicious entries for admin review

**Frontend**:  
- HTML Templates  
- CSS (mobile-first, responsive)  
- JavaScript + HTMX

**Testing**:  
- `pytest`, `pytest-cov`  
- Unit, integration, end-to-end tests

**Security**:  
- Basic auth for admin  
- Data integrity checks (flagging invalid data instead of deletion)  
- Conservative rate limiting for scraping

---

## Database Schema

**Stipends**:  
- `id`, `name`, `summary`, `description`, `homepage_url`, `application_procedure`, `eligibility_criteria`, `application_deadline`, `open_for_applications`, `created_at`, `updated_at`  
- M2M with `Tags` and `Organizations`

**Organizations**:  
- `id`, `name`, `description`, `homepage_url`, `created_at`, `updated_at`

**Tags**:  
- `id`, `name`, `category`  
- M2M with `Stipends`

**Users**:  
- `id`, `username`, `password_hash`, `email`, `is_admin`, `created_at`, `updated_at`

**Bots**:  
- `id`, `name`, `description`, `status`, `last_run`, `error_log`

**Notifications**:  
- `id`, `message`, `type`, `read_status`, `created_at`

---

## System Components

**Database Initialization**:  
- `app.py` sets up the database, runs migrations, creates default admin user.

**User-Facing Pages (Public Routes)**:  
- Homepage: Popular stipends, tag filters  
- Stipend Search: HTMX-powered filtering and keyword search  
- Details Page: Full stipend info, eligibility, related orgs

**Admin Section**:  
- Basic auth login  
- CRUD routes for stipends, tags, organizations, users, bots  
- Bot management dashboard, notifications for flagged entries

**Automated Bots**:  
- `TagBot`, `UpdateBot`, `ReviewBot`  
- Admin-scheduled runs, logs, error reporting

---

## Coding Conventions

- **PEP 8**: Follow Python PEP 8 style  
- **Modularity**: Keep code small and focused  
- **Clear Separation**: Models, services, routes, and templates well-structured  
- **Documentation**: Docstrings, comments, and meaningful names

---

## Coding Practices

1. **Small, Frequent Commits** with descriptive messages  
2. **Test-Driven Development** where possible  
3. **Error Handling & Logging**: Don’t just `print` stack traces, sir  
4. **Code Reviews**: Peer review before merging

---

## Testing Specification

- `pytest` and `pytest-cov` for test execution and coverage  
- Aim for **80%+** coverage  
- Test hierarchy: unit > integration > end-to-end  
- Mirror app structure in `tests/`

Use fixtures, in-memory DB, and the Flask test client for isolation.

---

## Environment and Configuration

- `.env.example` template for environment variables  
- Load vars with `python-dotenv`  
- Use distinct configs for dev, test, production  
- Initialize default admin user from env vars

Variables like `SECRET_KEY`, `DATABASE_URL`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `ADMIN_EMAIL`, and `FLASK_CONFIG` should be set in `.env`.

---

## Security Considerations

- Auth-check all admin routes  
- Validate & sanitize inputs  
- Keep dependencies up-to-date  
- Store passwords as salted hashes (no plain-text nonsense, sir)

---

## System Flow

1. **Bots Update Data**: Populate and refine stipend data  
2. **Users Interact**: Filter and view stipends in real-time via HTMX  
3. **Admins Manage**: Add/edit stipends, handle flagged data, schedule bots

---

## Collaboration Guidelines

- **Branching**: Feature branches for new functionality  
- **Pull Requests**: Required code reviews  
- **Commit Messages**: Descriptive, small increments

---

## Documentation

- **README.md**: Overview, setup steps, dependency list  
- **CONVENTIONS.md**: Coding standards  
- **Docstrings & Comments**: For complex logic

---

## Folder Structure

```plaintext
Project Root/
  .env.example
  .flaskenv
  .gitignore
  CONVENTIONS.md            # Coding standards and conventions
  PROJECT.md                # Proposed project structure and guidelines
  alembic.ini
  app.py
  requirements.txt
  pytest.ini
  app/
    __init__.py
    config.py
    extensions.py
    utils.py
    models/
      __init__.py
      association_tables.py
      bot.py
      notification.py
      organization.py
      stipend.py
      tag.py
      user.py
    routes/
      __init__.py
      admin/
        __init__.py
        bot_routes.py
        organization_routes.py
        stipend_routes.py
        tag_routes.py
        user_routes.py
      user_routes.py        # Authenticated user routes
      public_routes.py      # Public-facing routes (previously visitor_routes)
    services/
      __init__.py
      bot_service.py
      notification_service.py
      organization_service.py
      stipend_service.py
      tag_service.py
      user_service.py
    forms/
      __init__.py
      user_forms.py
      admin_forms.py
    templates/
      base.html
      public/               # Templates for public-facing pages
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
  bots/
    tag_bot.py
    update_bot.py
    review_bot.py
  migrations/
    ...
  instance/
    site.db
    config.env
  tests/
    conftest.py
    app/
      __init__.py
      test_config.py
      test_extensions.py
      test_utils.py
      models/
        __init__.py
        test_*.py
      routes/
        __init__.py
        admin/
          __init__.py
          test_*.py
        test_public_routes.py
        test_user_routes.py
      services/
        __init__.py
        test_*.py
      forms/
        __init__.py
        test_*.py
    bots/
      __init__.py
      test_*.py
  README.md
```

---

## Additional Components

- **Logging & Monitoring**: Use Python’s `logging`. Consider log rotation.  
- **Deployment**: Docker or Platform services. Use PostgreSQL in production.  
- **Backups & Recovery**: Regular DB backups.  
- **Performance**: Index DB columns, minify CSS/JS, etc.  
- **Migrations**: Alembic-managed, committed to version control.



