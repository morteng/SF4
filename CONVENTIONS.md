## Coding Conventions
- Use Flask's built-in flash messaging system with `FlashMessages` and `FlashCategory` enums
- Implement robust error handling with try-except blocks and logging
- Use type hints for better code clarity and IDE support
- Maintain logging with clear, structured messages using `logger`
- Use bleach for input sanitization with specific allowed tags
- Keep CSS in `app/static/css/main.css` and JS in `app/static/js/main.js`
- Use Tailwind for styling and HTMX for dynamic interactions
- Validate all form inputs both client and server side
- Use `Enum` for constants to ensure type safety
- Add docstrings to all classes and functions
- Centralize test utilities in `tests/utils.py`
- Use factory functions for test data creation

## TODO.md
- This file must be updated every time we do any file updates so that it always reflects our goal, plan and tasks. Always use full paths when referencing files to avoid confusion. This is a memory store for you, so jot down any salient thoughts about tests or code you would like to keep in mind for later. If you learn something about the codebase that would be good to know later, include the knowledge here. Do this after editing any other files. Always update TODO.md.

# DIARY.md
- This file is a summary of our notable achievements. If it gets too long, collaps and summarise it. Any key learnings that are new should be added to the TODO.md files knowledge. 

# VALIDATION.md
- A summary of our validation tests. Update it and expand it when you need to.

