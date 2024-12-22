## Goal
Refactor the code to use a centralized flash messaging system and ensure all tests are updated accordingly.

## plan
1. Create a new utility function in `app/utils.py` to handle flash messages.
2. Update all routes in `app/routes/admin/bot_routes.py`, `app/routes/admin/organization_routes.py`, `app/routes/admin/stipend_routes.py`, `app/routes/admin/tag_routes.py`, and `app/routes/admin/user_routes.py` to use the new utility function for flash messaging.
3. Ensure that flash messages are only included in `base.html`.
4. Update all tests that use flash messages to ensure they work with the new centralized flash messaging system.

## tasks
- [ ] Create a new utility function in `app/utils.py` to handle flash messages.
- [ ] Update all routes in `app/routes/admin/bot_routes.py` to use the new utility function for flash messaging.
- [ ] Update all routes in `app/routes/admin/organization_routes.py` to use the new utility function for flash messaging.
- [ ] Update all routes in `app/routes/admin/stipend_routes.py` to use the new utility function for flash messaging.
- [ ] Update all routes in `app/routes/admin/tag_routes.py` to use the new utility function for flash messaging.
- [ ] Update all routes in `app/routes/admin/user_routes.py` to use the new utility function for flash messaging.
- [ ] Ensure that flash messages are only included in `base.html`.
- [ ] Update all tests that use flash messages to ensure they work with the new centralized flash messaging system.
  - [ ] Update tests in `tests/test_bot_routes.py`
  - [ ] Update tests in `tests/test_organization_routes.py`
  - [ ] Update tests in `tests/test_stipend_routes.py`
  - [ ] Update tests in `tests/test_tag_routes.py`
  - [ ] Update tests in `tests/test_user_routes.py`
