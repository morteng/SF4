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

## Bots
- Core CRUD and scheduling implemented
- Admin interface for bot management
- Basic scheduling operational

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

## Lessons Learned

### Validation Improvements
- Fixed `TypeError` in `CustomDateTimeField` caused by incorrect `format` parameter handling
- Consolidated leap year validation logic to avoid redundancy
- Improved error message consistency using constants from `app/constants.py`
- Added comprehensive tests for edge cases in date/time validation

### Error Handling
- Ensured all error messages are centralized in `app/constants.py`
- Standardized error message format across all fields
- Improved validation error reporting

### Testing
- Added comprehensive test coverage for date/time validation
- Verified edge cases in date/time validation
- Improved test isolation and reliability

## System Components

**Database Initialization**:  
- `app.py` sets up the database, runs migrations, creates default admin user.

**Core Architecture**:
- BaseRouteController handles common CRUD operations for all admin routes
- BaseService provides common CRUD operations for all services
- BaseCRUDTest provides common test cases for all services

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
3. **Error Handling & Logging**: Don’t just `print` stack traces  
4. **Code Reviews**: Peer review before merging  
5. **DRY Principle**: Reuse code through base classes and utilities  
6. **Shared Test Utilities**: Use common test helpers and base classes  
7. **Service Layer Consistency**: Follow base service patterns

---

## Testing Specification

- `pytest` and `pytest-cov` for test execution and coverage  
- Aim for **80%+** coverage  
- Test hierarchy: unit > integration > end-to-end  
- Mirror app structure in `tests/`
- All flash messages must use messages defined in app\constants.py - create new additions here when needed. All tests should evaluate the constant used, not the string itself.

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

## routes
Endpoint                     Methods    Rule
---------------------------  ---------  ------------------------------------
admin.bot.create             GET, POST  /admin/bots/create
admin.bot.delete             POST       /admin/bots/<int:id>/delete
admin.bot.edit               GET, POST  /admin/bots/<int:id>/edit
admin.bot.index              GET        /admin/bots/
admin.bot.run                POST       /admin/bots/<int:id>/run
admin.bot.schedule           POST       /admin/bots/<int:id>/schedule       
admin.dashboard.dashboard    GET        /admin/dashboard/
admin.organization.create    GET, POST  /admin/organizations/create
admin.organization.delete    POST       /admin/organizations/<int:id>/delete
admin.organization.edit      GET, POST  /admin/organizations/<int:id>/edit  
admin.organization.index     GET        /admin/organizations/
admin.organization.paginate  GET        /admin/organizations/paginate       
admin.organization.view      GET        /admin/organizations/<int:id>       
admin.stipend.create         GET, POST  /admin/stipends/<int:id>/edit       
admin.stipend.delete         POST       /admin/stipends/<int:id>/delete     
admin.stipend.edit           GET, POST  /admin/stipends/<int:id>/edit
admin.stipend.index          GET        /admin/stipends/
admin.stipend.paginate       GET        /admin/stipends/paginate
admin.tag.create             GET, POST  /admin/tags/create
admin.tag.delete             POST       /admin/tags/<int:id>/delete
admin.tag.edit               GET, POST  /admin/tags/<int:id>/edit
admin.tag.index              GET        /admin/tags/
admin.tag.paginate           GET        /admin/tags/paginate
admin.user.create            GET, POST  /admin/users/create
admin.user.delete            POST       /admin/users/<int:id>/delete
admin.user.edit              GET, POST  /admin/users/<int:id>/edit
admin.user.edit_profile      GET, POST  /admin/users/edit_profile
admin.user.index             GET        /admin/users/
admin.user.reset_password    POST       /admin/users/<int:id>/reset_password
admin.user.toggle_active     POST       /admin/users/<int:id>/toggle_active
public.filter_stipends       POST       /filter
public.index                 GET        /
public.login                 GET, POST  /login
public.logout                GET        /logout
public.register              GET, POST  /register
static                       GET        /static/<path:filename>
user.edit_profile            GET, POST  /user/profile/edit
user.profile                 GET        /user/profile

---

## Additional Components

- **Logging & Monitoring**: Use Python’s `logging`. Consider log rotation.  
- **Deployment**: Docker or Platform services. Use PostgreSQL in production.  
- **Backups & Recovery**: Regular DB backups.  
- **Performance**: Index DB columns, minify CSS/JS, etc.  
- **Migrations**: Alembic-managed, committed to version control.



# Project Specification: Stipend Discovery Website

## Key Updates
- **Validation Improvements**:
  - Enhanced time validation in `CustomDateTimeField`
  - Standardized error messages for date/time fields
  - Improved test coverage for form validation scenarios

## Technical Updates
- Fixed failing tests for time validation
- Reduced code duplication in form validation
- Improved error message consistency

## Lessons Learned

### Validation Improvements
- Consolidated leap year validation logic in `CustomDateTimeField` to avoid redundancy.
- Fixed `TypeError` caused by incorrect usage of `self.format` in `datetime.strptime`.
- Improved error handling for invalid dates and times.

### Error Handling
- Ensured all error messages are centralized in `app/constants.py` and used consistently across the codebase.

### Testing
- Added comprehensive tests for edge cases in `CustomDateTimeField`, including leap years, invalid time components, and missing fields.

## New Section: Lessons Learned
- **Validation Improvements**:
  - Consolidated leap year validation logic in `CustomDateTimeField` to avoid redundancy.
  - Fixed `TypeError` caused by incorrect usage of `self.format` in `datetime.strptime`.
  - Improved error handling for invalid dates and times.

- **Error Handling**:
  - Ensured all error messages are centralized in `app/constants.py` and used consistently across the codebase.

- **Testing**:
  - Added comprehensive tests for edge cases in `CustomDateTimeField`, including leap years, invalid time components, and missing fields.

## System Components
- **Forms**:
  - Updated `CustomDateTimeField` to support custom error messages.
  - Added `DataRequired` validator to `application_deadline` in `StipendForm`.

## Testing Specification
- Added more test cases for edge cases in form validation.
- Verified error message fallbacks for required fields.

## Technical Updates
- Fixed failing tests for date validation
- Reduced code duplication in admin routes
- Improved test coverage for form validation
- **Fixed `CustomDateTimeField` Initialization**:
  - Resolved the `TypeError` caused by duplicate `format` parameter in `CustomDateTimeField`.
  - Updated `StipendForm` to avoid passing the `format` parameter explicitly.
- **Improved Validation**:
  - Enhanced date/time validation logic in `CustomDateTimeField` to handle edge cases (e.g., leap years, invalid time components).
  - Standardized error messages using constants from `app/constants.py`.
- **Lessons Learned**:
  - Always ensure parameters are not passed multiple times during field initialization.
  - Use centralized error messages from `app/constants.py` for consistency.
  - Test edge cases thoroughly, especially for date/time validation.

## Technical Stack
- Backend: Flask, SQLite/PostgreSQL, Alembic, HTMX
- Frontend: HTML, CSS, JavaScript
- Testing: pytest, pytest-cov
- Security: Basic auth, data integrity checks

## Database Schema
Core tables: Stipends, Organizations, Tags, Users, Bots, Notifications

## System Components
- Database Initialization
- Core Architecture (Base classes for routes, services, tests)
- User-Facing Pages
- Admin Section
- Automated Bots

## Coding Practices
- Small, frequent commits
- Test-Driven Development
- Error Handling & Logging
- Code Reviews
- DRY Principle



