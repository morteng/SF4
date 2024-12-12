## routes
Endpoint                   Methods    Rule
-------------------------  ---------  ------------------------------------
admin.bot.create           GET, POST  /admin/bots/create
admin.bot.delete           POST       /admin/bots/<int:id>/delete
admin.bot.index            GET        /admin/bots/
admin.bot.run              POST       /admin/bots/<int:id>/run
admin.bot.update           GET, POST  /admin/bots/<int:id>/update
admin.dashboard.dashboard  GET        /admin/dashboard/dashboard
admin.organization.create  GET, POST  /admin/organizations/create
admin.organization.delete  POST       /admin/organizations/<int:id>/delete
admin.organization.index   GET        /admin/organizations/
admin.organization.update  GET, POST  /admin/organizations/<int:id>/update
admin.stipend.create       GET, POST  /admin/stipends/create
admin.stipend.delete       POST       /admin/stipends/<int:id>/delete
admin.stipend.index        GET        /admin/stipends/
admin.stipend.update       GET, POST  /admin/stipends/<int:id>/update
admin.tag.create           GET, POST  /admin/tags/create
admin.tag.delete           POST       /admin/tags/<int:id>/delete
admin.tag.index            GET        /admin/tags/
admin.tag.update           GET, POST  /admin/tags/<int:id>/update
admin.user.create          GET, POST  /admin/users/create
admin.user.delete          POST       /admin/users/<int:id>/delete
admin.user.index           GET        /admin/users/
admin.user.update          GET, POST  /admin/users/<int:id>/update
public.index               GET        /
public.login               GET, POST  /login
public.logout              GET        /logout
static                     GET        /static/<path:filename>
user.edit_profile          GET, POST  /user/profile/edit
user.profile               GET        /user/profile

## notes
- Use session.get() instead of query.get() for better performance and to avoid potential issues with the query cache.
- All admin routes have an admin. prefix, as in admin.stipend.create or admin.dashboard.dashboard.
- keep all css in app\static\css\main.css and all javascript in app\static\js\main.js