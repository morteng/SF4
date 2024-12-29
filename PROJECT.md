# Project Specification: Stipend Discovery Website

## Key Updates
- Fixed error message handling in CustomDateTimeField
- Standardized validation error messages across all form fields
- Removed hardcoded error messages in favor of configurable ones
- Improved test coverage for form validation
- Addressed datetime.utcnow() deprecation warnings

## Technical Updates
- Fixed failing tests for date validation
- Reduced code duplication in admin routes
- Improved test coverage for form validation

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



