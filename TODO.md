# TODO List

## Current Goals
1. **Complete Admin System Refactoring**
   - [ ] Implement caching for frequently accessed data
   - [ ] Add bulk actions (delete, update) for stipends, tags, and organizations
   - [ ] Add search and filtering functionality to index pages
   - [ ] Add export functionality (CSV, Excel) for all admin data
   - [ ] Implement audit logging for admin actions

## Knowledge & Memories
- **Template Structure**
  * All admin templates should extend `base.html` directly
  * Forms use consistent styling and error handling
  * Flash messages are displayed using `_flash_messages.html`
  * Buttons use standardized macros from `_macros.html`

- **Testing Best Practices**
  * Use fixtures for common test setup
  * Verify template rendering in route tests
  * Check for proper error handling
  * Test both success and failure cases

