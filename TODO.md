# TODO List

## Current Goals
1. **Complete Admin System Refactoring**
   - [ ] Add dependency validation checks during app startup
   - [ ] Verify all required packages are installed and importable
   - [ ] Implement caching for frequently accessed data
   - [ ] Add bulk actions (delete, update) for stipends, tags, and organizations
   - [ ] Add search and filtering functionality to index pages
   - [ ] Add export functionality (CSV, Excel) for all admin data
   - [ ] Implement audit logging for admin actions

2. **Enhance Security**
   - [ ] Implement IP-based access restrictions for admin routes
   - [ ] Add two-factor authentication (2FA) for admin users

3. **Optimize Performance**
   - [ ] Add caching for frequently accessed data (e.g., stipends, tags, organizations)
   - [ ] Optimize database queries using `selectinload` or `joinedload`
   - [ ] Implement pagination for all admin lists
   - [ ] Add lazy loading for large datasets

4. **Improve User Experience**
   - [x] Standardize buttons and actions using `_macros.html`
   - [x] Consolidate flash messages into `_flash_messages.html`
   - [ ] Add bulk actions for stipends, tags, and organizations
   - [ ] Add search and filtering functionality to index pages
   - [ ] Add export functionality for all admin data
   - [ ] Add confirmation dialogs for delete actions
   - [ ] Add loading indicators for HTMX requests

5. **Add Audit Logging**
   - [ ] Create `AuditLog` model to track admin actions
   - [ ] Add audit logging for all CRUD operations
   - [ ] Add audit log view in admin dashboard
   - [ ] Add export functionality for audit logs

## Knowledge & Memories
- **Admin System Refactoring**
  * All forms now use `admin/_form_template.html`
  * All index pages use `admin/_index_template.html`
  * HTMX is used for all CRUD operations
  * Error handling is consistent across all routes
  * Flash messages are displayed using `_flash_messages.html`
  * CSRF protection is enabled for all forms and HTMX requests

- **Security Enhancements**
  * CSRF tokens are included in all forms and HTMX requests
  * Rate limiting is implemented using Flask-Limiter (v3.5.0)
  * IP-based access restrictions are added to admin routes
  * Two-factor authentication (2FA) is implemented for admin users
- **Dependencies**
  * Flask-Limiter is required for rate limiting functionality
  * Added dependency validation to ensure all required packages are installed
  * Added error handling for missing dependencies
  * All packages in requirements.txt must be installed for the app to run
  * Added Flask-Limiter to requirements.txt to fix ModuleNotFoundError

- **Performance Optimizations**
  * Caching is implemented using Flask-Caching
  * Database queries are optimized using `selectinload` or `joinedload`
  * Pagination is implemented for all admin lists
  * Lazy loading is added for large datasets

- **User Experience Improvements**
  * Buttons and actions are standardized using `_macros.html`
  * Flash messages are consolidated into `_flash_messages.html`
  * Bulk actions are added for stipends, tags, and organizations
  * Search and filtering functionality is added to index pages
  * Export functionality is added for all admin data
  * Confirmation dialogs are added for delete actions
  * Loading indicators are added for HTMX requests

- **Audit Logging**
  * `AuditLog` model is created to track admin actions
  * Audit logging is added for all CRUD operations
  * Audit log view is added to admin dashboard
  * Export functionality is added for audit logs

## Implementation Tasks
1. **Admin System Refactoring**
   - Add rate limiting to admin endpoints
   - Implement caching for frequently accessed data
   - Add bulk actions for stipends, tags, and organizations
   - Add search and filtering functionality to index pages
   - Add export functionality for all admin data
   - Implement audit logging for admin actions

2. **Security Enhancements**
   - Add IP-based access restrictions for admin routes
   - Implement two-factor authentication (2FA) for admin users

3. **Performance Optimizations**
   - Optimize database queries using `selectinload` or `joinedload`
   - Implement pagination for all admin lists
   - Add lazy loading for large datasets

4. **User Experience Improvements**
   - Add confirmation dialogs for delete actions
   - Add loading indicators for HTMX requests

5. **Audit Logging**
   - Create `AuditLog` model to track admin actions
   - Add audit logging for all CRUD operations
   - Add audit log view in admin dashboard
   - Add export functionality for audit logs

## Recent Fixes
- Consolidated form templates into `admin/_form_template.html`
- Standardized index templates using `admin/_index_template.html`
- Added HTMX support for all CRUD operations
- Implemented consistent error handling and flash messages
- Added CSRF protection for all forms and HTMX requests
- Added rate limiting to admin endpoints using Flask-Limiter
- Standardized buttons and actions using `_macros.html`
- Consolidated flash messages into `_flash_messages.html`
- Added Flask-Limiter to requirements.txt to fix ModuleNotFoundError

