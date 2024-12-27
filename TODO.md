# TODO List

## Current Goals
1. **Complete Admin System Refactoring**
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
   - [ ] Add bulk actions for stipends, tags, and organizations
   - [ ] Add search and filtering functionality to index pages
   - [ ] Add export functionality for all admin data
   - [ ] Add confirmation dialogs for delete actions
   - [ ] Add loading indicators for HTMX requests

## New Goals from Testing
5. **Fix Template Issues**
   - [x] Fix template inheritance in bot create template (changed from admin/_base.html to base.html)

6. **Improve Test Coverage**
   - [x] Add tests for bot routes
   - [ ] Increase coverage for admin routes
   - [ ] Add integration tests for bot operations

## Knowledge & Memories
- **Template Structure**
  * All admin templates should extend `base.html`
  * Forms use consistent styling and error handling
  * Flash messages are displayed using `_flash_messages.html`
  * Buttons use standardized macros from `_macros.html`

- **Testing Best Practices**
  * Use fixtures for common test setup
  * Verify template rendering in route tests
  * Check for proper error handling
  * Test both success and failure cases

## Knowledge & Memories
- **Template Structure**
  * All admin templates extend `admin/_base.html`
  * Forms use consistent styling and error handling
  * Flash messages are displayed using `_flash_messages.html`
  * Buttons use standardized macros from `_macros.html`

- **Testing Best Practices**
  * Use fixtures for common test setup
  * Verify template rendering in route tests
  * Check for proper error handling
  * Test both success and failure cases

