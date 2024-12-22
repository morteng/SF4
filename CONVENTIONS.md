## routes
Endpoint                   Methods    Rule
-------------------------  ---------  ------------------------------------       
admin.bot.create           GET, POST  /admin/bots/create
admin.bot.delete           POST       /admin/bots/<int:id>/delete
admin.bot.edit             GET, POST  /admin/bots/<int:id>/edit
admin.bot.index            GET        /admin/bots/
admin.bot.run              POST       /admin/bots/<int:id>/run
admin.dashboard.dashboard  GET        /admin/dashboard/
admin.organization.create  GET, POST  /admin/organizations/create
admin.organization.delete  POST       /admin/organizations/<int:id>/delete       
admin.organization.edit    GET, POST  /admin/organizations/<int:id>/edit
admin.organization.index   GET        /admin/organizations/
admin.stipend.create       GET, POST  /admin/stipends/create
admin.stipend.delete       POST       /admin/stipends/<int:id>/delete
admin.stipend.edit         GET, POST  /admin/stipends/<int:id>/edit
admin.stipend.index        GET        /admin/stipends/
admin.tag.create           GET, POST  /admin/tags/create
admin.tag.delete           POST       /admin/tags/<int:id>/delete
admin.tag.edit             GET, POST  /admin/tags/<int:id>/edit
admin.tag.index            GET        /admin/tags/
admin.user.create          GET, POST  /admin/users/create
admin.user.delete          POST       /admin/users/<int:id>/delete
admin.user.edit            GET, POST  /admin/users/<int:id>/edit
admin.user.index           GET        /admin/users/
public.index               GET        /
public.login               GET, POST  /login
public.logout              GET        /logout
public.register            GET, POST  /register
static                     GET        /static/<path:filename>
user.edit_profile          GET, POST  /user/profile/edit
user.login                 GET, POST  /user/login
user.profile               GET        /user/profile

## testing
In your tests, evaluating flash messages involves the following steps:

Trigger an Action: Perform a POST or GET request that should generate flash messages (e.g., creating or updating an organization).

Access the Session: Use session_transaction() to access the test client's session data.

Retrieve Flashed Messages: Extract the '_flashes' list from the session, which contains tuples of (category, message).

Assert Messages: Check that the expected flash message and its category (e.g., 'success', 'error') are present in the '_flashes' list.

Example:

with logged_in_admin.session_transaction() as sess:
    flashed_messages = sess.get('_flashes', [])
assert any(
    cat == 'success' and msg == "Expected success message."
    for cat, msg in flashed_messages
)

This ensures that your application correctly sets and displays flash messages in response to user actions.

## notes
- Use session.get() instead of query.get() for better performance and to avoid potential issues with the query cache.
- All admin routes have an admin. prefix, as in admin.stipend.create or admin.dashboard.dashboard.
- keep all css in app\static\css\main.css and all javascript in app\static\js\main.js 
- Use tailwind and htmx whenever possible