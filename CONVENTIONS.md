## Coding Conventions
### Testing
- Type hints & docstrings required
- Use fixtures & parameterized tests
- Verify UI & DB state
- Use enums (FlashCategory, FlashMessages) for assertions
- Use factory functions (tests/utils.py)

### Security
- Validate all inputs
- CSRF tokens required
- Rate limit sensitive endpoints
- Sanitize with bleach

### Code Organization
- CSS: Tailwind in main.css
- JS: HTMX in main.js
- Constants: Use FlashCategory enum for message types

