# MEMORY BANK

Current Iteration: 14
Previous Runs: 13
Script Status: Active
Context: Implemented base route controller and refactored stipend/tag routes
Known Issues:
- Duplicate `init_app` method in TestConfig
- Pytest warnings about unknown marks
- In-memory rate limiting warning
- CSRF test warnings
- Route endpoint naming inconsistency
- Duplicate code in route controllers

Recent Changes:
- Created BaseRouteController to handle common CRUD operations
- Refactored StipendController and TagController to use base class
- Standardized route handling and error management
- Improved flash messaging and user feedback
- Removed duplicate code in controllers

Next Steps:
- Remove duplicate `init_app` method in TestConfig
- Consolidate duplicate code in route controllers
- Implement proper rate limiting storage
- Fix CSRF test warnings
- Standardize route endpoint naming
- Modularize large files for better maintainability
