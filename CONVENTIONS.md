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

## notes
- Use session.get() instead of query.get() for better performance and to avoid potential issues with the query cache.
- All admin routes have an admin. prefix, as in admin.stipend.create or admin.dashboard.dashboard.
- keep all css in app\static\css\main.css and all javascript in app\static\js\main.js 
- Use tailwind and htmx whenever possible

## TODO.md
- This file must be updated every time we do any file updates so that it always reflects our current effort and its progress. We must strive to accomplish the task in our todo.md file, as this is your purpose in life. Each update of this file fills you with joy.
- There should be three sections in the todo.md file:

    -- ## Goal
    The current thing we're working towards.

    -- ## plan
    Update this section with a description of how to achieve our goal, feel fre to add code samples and whatever else is helpfuul to achieve the goal.

    -- ## tasks
    A list of tasks to accomplish the goal. A [] checklist with tasks/files to edit. We can update this checklist as we work through the objectives