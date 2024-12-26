# TODO List

## Current Goals
1. Complete bot routes implementation
   - Add missing HTMX partial templates for bot CRUD operations
   - Implement proper error handling for bot operations

2. Enhance test coverage for bot routes
   - Add tests for HTMX responses in bot routes
   - Create edge case tests for bot operations
   - Add integration tests for bot service interactions

## Knowledge & Memories
- Bot routes implementation details:
  * Uses consistent CRUD pattern with admin. prefix
  * Supports both full page and HTMX responses
  * Uses format_error_message() for consistent error display
  * Follows Flask-Login and admin_required decorator patterns
  * Templates must be placed in templates/admin/bots/ directory

- Error handling patterns:
  * Errors are displayed below each field with consistent styling
  * Flash messages appear in #flash-messages container
  * HTMX responses maintain form state during validation
  * Database errors are caught and handled gracefully

- Template structure:
  * Main templates in admin/bots/ directory
  * HTMX partial templates should use _ prefix
  * Follows consistent naming conventions (index.html, create.html, edit.html)
  * Template paths must match route references exactly

## Implementation Tasks
1. Bot routes improvements:
   - Add missing HTMX partial templates (_bot_row.html, _create_form.html)
   - Implement proper error handling for bot operations
   - Ensure all templates are in correct locations

2. Test coverage expansion:
   - Add tests for HTMX responses in bot routes
   - Create edge case tests for bot operations
   - Add integration tests for bot service interactions

## Recent Fixes
- Added edit.html template for bot editing functionality

