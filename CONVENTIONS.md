## Coding Conventions
### Testing
- Use type hints consistently in test functions
- Add detailed docstrings explaining test purpose
- Use fixtures for common setup (e.g., authenticated_admin)
- Parameterize tests for multiple scenarios
- Verify both UI responses and database state
- Include edge case and error scenario tests
- Use logging for test execution tracking
- Centralize test utilities in tests/utils.py

### Security
- Validate all form inputs client and server side
- Use CSRF tokens for all forms
- Implement rate limiting for sensitive endpoints
- Use bleach for input sanitization
- Use Enum for constants to ensure type safety

### Code Organization
- Keep CSS in app/static/css/main.css
- Keep JS in app/static/js/main.js
- Use Tailwind for styling
- Use HTMX for dynamic interactions
- Maintain clear separation between routes, models, and services

## TODO.md
- This file must be updated every time we do any file updates so that it always reflects our goal, plan and tasks. Always use full paths when referencing files to avoid confusion. This is a memory store for you, so jot down any salient thoughts about tests or code you would like to keep in mind for later. If you learn something about the codebase that would be good to know later, include the knowledge here. Do this after editing any other files. Always update TODO.md.

# DIARY.md
- This file is a summary of our notable achievements. If it gets too long, collaps and summarise it. Any key learnings that are new should be added to the TODO.md files knowledge. 

# VALIDATION.md
- A summary of our validation tests. Update it and expand it when you need to.

