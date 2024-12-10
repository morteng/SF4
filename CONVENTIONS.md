
## notes
- Use session.get() instead of query.get() for better performance and to avoid potential issues with the query cache.
- All admin routes have an admin. prefix, as in admin.admin_stipend.create or admin.dashboard.dashboard.
- keep all css in app\static\css\main.css and all javascript in app\static\js\main.js