## Goal
Refactor the code to use a centralized flash messaging system.

## plan
1. Create a new utility function in `app/utils.py` to handle flash messages.
2. Update all routes in `app/routes/admin/bot_routes.py`, `app/routes/admin/organization_routes.py`, `app/routes/admin/stipend_routes.py`, `app/routes/admin/tag_routes.py`, and `app/routes/admin/user_routes.py` to use the new utility function for flash messaging.

## tasks
- [x] Create a new utility function in `app/utils.py` to handle flash messages.
- [x] Update all routes in `app/routes/admin/bot_routes.py` to use the new utility function for flash messaging.
- [x] Update all routes in `app/routes/admin/organization_routes.py` to use the new utility function for flash messaging.
- [x] Update all routes in `app/routes/admin/stipend_routes.py` to use the new utility function for flash messaging.
- [x] Update all routes in `app/routes/admin/tag_routes.py` to use the new utility function for flash messaging.
- [x] Update all routes in `app/routes/admin/user_routes.py` to use the new utility function for flash messaging.
