# Stipend Discovery Website: **Complete Project Specification**

## 1. Overview
The **Stipend Discovery Website** is a Flask-based web application that helps users discover and filter stipends in real time. It features:

- A **user-facing interface** for searching and applying filters via HTMX (no full-page reloads).
- An **admin portal** for secure CRUD operations on stipends, tags, organizations, users, and automated bots.
- **Automated bots** that handle scraping, data updates, tagging, and content validation (keeping everything neat and fresh).
- Thorough **testing** from the ground up with `pytest` and a built-in dependency verification to make sure the environment is (mostly) foolproof.

---

## 2. Key Features
1. **User-Facing Discovery**  
   - Search and filter stipends dynamically (HTMX for partial page updates).  
   - Mobile-first, responsive templates.

2. **Admin Interface**  
   - Secure routes requiring auth.  
   - CRUD functionality for stipends, tags, organizations, users, and bots.  
   - Scheduling and running bots directly from the dashboard.

3. **Automated Bots**  
   - **TagBot**: Applies consistent tagging.  
   - **UpdateBot**: Checks for new or updated stipend info.  
   - **ReviewBot**: Flags questionable or outdated entries.  
   - Admin-scheduled runs with logs and error reporting.

4. **Testing & Quality Checks**  
   - Tests run on startup to ensure dependencies are installed and code is up to snuff.  
   - Comprehensive coverage for date/time validations, user flows, and database interactions.

5. **Dynamic Content Updates**  
   - Leveraging HTMX so users can see new filters, updated lists, etc., without a full-page reload.

---

## 3. Technical Stack

| Component    | Tech                 | Notes                                                   |
|--------------|----------------------|---------------------------------------------------------|
| **Backend**  | **Flask** (Python)   | Central server logic, routes, forms, etc.              |
| **Database** | SQLite (dev) / PostgreSQL (prod) | Alembic for migrations                              |
| **Frontend** | HTML, CSS, JS, HTMX  | HTMX for partial page updates, responsive layout        |
| **Testing**  | `pytest`, `pytest-cov`, `freezegun` | High coverage, mocking for date/time consistency |
| **Other**    | Python-dotenv        | Loads environment variables; distinct configs per env   |

### Environment & Configuration
- Use `.env.example` to generate a local `.env`.
- Key environment variables:
  - `SECRET_KEY`, `DATABASE_URL`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `ADMIN_EMAIL`, `FLASK_CONFIG`
- Switch out SQLite for PostgreSQL in production.
- Admin user is created automatically if the corresponding env variables are present.

---

## 4. Project Architecture

1. **Core Structure**  
   - `app/__init__.py` (initializes Flask app, DB connections, etc.)  
   - `app/models/`: SQLAlchemy models.  
   - `app/services/`: Common business logic (e.g., `BaseService`, specialized services).  
   - `app/routes/`: All route controllers (public vs. admin).  
   - `app/common/utils.py`: Shared utility functions (to avoid circular imports).  
   - `app/constants.py`: Central repository for error messages and magic strings.  

2. **Bots**  
   - Implemented in `app/services/bot_service.py` (and friends).  
   - Schedules, logs, and error reporting are all accessible via the admin dashboard.

3. **Startup Quality Checks**  
   - Test suite is triggered automatically (or can be triggered with `pytest`).  
   - Dependencies verified with a pre-test script (`verify_dependencies()` in `tests/conftest.py`).

---

## 5. Database Schema

### Stipends

id (PK)
name
summary
description
homepage_url
application_procedure
eligibility_criteria
application_deadline (DateTime)
open_for_applications (Boolean)
created_at (DateTime)
updated_at (DateTime)

- Many-to-Many with **Tags** and **Organizations**.

### Organizations

id (PK)
name
description
homepage_url
created_at (DateTime)
updated_at (DateTime)

- Many-to-Many with **Stipends**.

### Tags

id (PK)
name
category

- Many-to-Many with **Stipends**.

### Users

id (PK)
username
password_hash
email
is_admin (Boolean)
created_at (DateTime)
updated_at (DateTime)

- Basic authentication for admin interface.

### Bots

id (PK)
name
description
status
last_run (DateTime)
error_log (Text)


### Notifications

id (PK)
message
type
read_status (Boolean)
created_at (DateTime)

- Used for alerting admin about flagged stipends, errors, etc.

---

## 6. Routes

Below is a partial list for clarity. `public` routes are accessible to all, while `admin` routes require authentication.

### Public Routes
| Endpoint           | Methods       | URL                  | Notes                                          |
|--------------------|--------------|----------------------|------------------------------------------------|
| `public.index`     | GET          | `/`                  | Homepage, highlights popular stipends          |
| `public.filter_stipends` | POST   | `/filter`            | HTMX filtering, returns partial updates        |
| `public.login`     | GET, POST    | `/login`             | Basic login form                               |
| `public.logout`    | GET          | `/logout`            | Log out, obviously                             |
| `public.register`  | GET, POST    | `/register`          | User registration form                         |

### Admin Routes
| Endpoint                    | Methods       | URL                                       | Notes                                      |
|----------------------------|--------------|-------------------------------------------|--------------------------------------------|
| `admin.dashboard.dashboard`| GET          | `/admin/dashboard/`                       | Admin home page                            |
| `admin.stipend.index`      | GET          | `/admin/stipends/`                        | List all stipends                          |
| `admin.stipend.create`     | GET, POST    | `/admin/stipends/<int:id>/edit`           | Create or edit stipend                    |
| `admin.stipend.delete`     | POST         | `/admin/stipends/<int:id>/delete`         | Delete a stipend                          |
| `admin.tag.index`          | GET          | `/admin/tags/`                            | List tags                                  |
| `admin.tag.create`         | GET, POST    | `/admin/tags/create`                      | Create new tag                             |
| `admin.tag.delete`         | POST         | `/admin/tags/<int:id>/delete`             | Delete a tag                               |
| `admin.bot.index`          | GET          | `/admin/bots/`                            | List bots (tagging, scraping, etc.)        |
| `admin.bot.create`         | GET, POST    | `/admin/bots/create`                      | Create new bot                             |
| `admin.bot.run`            | POST         | `/admin/bots/<int:id>/run`                | Run a bot immediately                     |
| `admin.bot.schedule`       | POST         | `/admin/bots/<int:id>/schedule`           | Schedule a bot to run later               |
| `admin.user.index`         | GET          | `/admin/users/`                           | List all users                             |
| `admin.user.create`        | GET, POST    | `/admin/users/create`                     | Create a user                              |
| ...                        | ...          | ...                                       | ...                                        |

(Additional endpoints exist for organizations and advanced tasks, but you get the idea, sir.)

---

## 7. Testing

### Framework & Tools
- **`pytest`**: Main test runner.  
- **`pytest-cov`**: Coverage reports. Aim for 80%+ coverage.  
- **`freezegun`**: For mocking date/time in tests—because we can’t rely on your system clock.  

### Strategy
1. **Unit Tests**: Small, isolated tests for services, models, and utilities.  
2. **Integration Tests**: Check routes and DB interactions (in-memory DB or test DB).  
3. **End-to-End Tests**: Full user flows, ensuring forms and HTMX partial updates behave.  
4. **Dependency Verification**: A pre-test script that checks if `pytest` and other packages are installed.

### Coverage
- Focus heavily on date/time validations, leap years, invalid formats, etc.  
- Stipend creation, editing, and deletion (both success and failure scenarios).  
- Admin flows, e.g., creating bots, running them, scheduling them.  
- Don’t forget negative tests: what if the user tries to pass a string instead of a date?

---

## 8. Recent Key Updates

1. **Validation Improvements**  
   - **CustomDateTimeField** now defaults to `InputRequired()` if no validators are passed.  
   - Centralized error messages in `app/constants.py`.  
   - Comprehensive date/time edge-case tests (leap years, invalid hours, etc.).

2. **Dependency Management**  
   - `pytest` added to `requirements.txt`.  
   - Pre-test check to ensure everything is installed before the test suite runs.

3. **Code Refactoring**  
   - Moved shared logic to `app/common/utils.py` to fix circular-import nightmares.  
   - `create_limit` property in `BaseService` now properly defined with getter/setter methods.

4. **Lessons Learned**  
   - Avoid hardcoding error messages all over the place; keep them in `app/constants.py`.  
   - Always define a property with `@property` before using `@<property>.setter`.  
   - Thorough testing of date/time validation is essential—particularly with user-submitted data.

---

## 9. Implementation Details

### Key Classes & Functions

- **`CustomDateTimeField`**  
  python
  class CustomDateTimeField(Field):
      def __init__(self, label=None, validators=None, **kwargs):
          if validators is None:
              validators = [InputRequired()]  # Default validator
          super().__init__(label=label, validators=validators, **kwargs)
          # Additional date/time parsing logic...
  
  - Ensures any form field based on this class has at least one validator by default.

- **`BaseService`**  
  python
  class BaseService:
      def __init__(self):
          self._create_limit = None

      @property
      def create_limit(self):
          return self._create_limit

      @create_limit.setter
      def create_limit(self, value):
          # Insert any validation or logging if needed
          self._create_limit = value
  
  - Common parent for various specialized services (StipendService, TagService, etc.).

- **`app/common/utils.py`**  
  - Shared methods that multiple modules need, e.g., `init_admin_user()`, date/time helpers, or wrapper functions to reduce code duplication.

### Circular Imports
- To avoid circular references (e.g., `app/__init__.py` importing a service that also imports `app`):
  - Put widely used functions in `app/common/utils.py`.
  - Use lazy imports inside functions that only need certain dependencies at runtime.

---

## 10. Security Considerations
- **Admin Routes**: Basic auth or token-based. Only logged-in, authorized users can access `/admin/...` endpoints.  
- **Password Hashing**: Use salted hashes (e.g., `bcrypt`). No plain-text nonsense, sir.  
- **Input Validation**: All forms should sanitize user input to prevent injection attacks.  
- **Rate Limiting**: For scraping and repeated requests.  
- **Regular Updates**: Keep dependencies updated to patch vulnerabilities.

---

## 11. System Flow

1. **Bots** scrape or update stipends in the background.  
2. **Users** visit the site, apply filters via HTMX for real-time updates.  
3. **Admins** log in, manage stipends, tags, organizations, users, and handle flagged data.  
4. **Notifications** alert admins about any errors or flagged entries.  
5. **Tests** run (preferably in CI) to confirm everything is in tip-top shape.

---

## 12. Coding Conventions
1. **PEP 8** for Python code style.  
2. **Docstrings** and meaningful variable names.  
3. **DRY Principle**: Consolidate repeated logic in `BaseService` or `app/common/utils.py`.  
4. **Log Errors**: No silent pass statements, sir—if something breaks, log it.  
5. **Test-Driven Development (TDD)** (if time and sanity permit).

---

## 13. Deployment
- **Docker** is recommended for containerizing.  
- **PostgreSQL** for production DB.  
- **Alembic** for DB migrations.  
- Consider a platform service (Heroku, AWS, etc.) for easy scaling.  
- Set up scheduled tasks (cron/worker) to run bots periodically.

---

## 14. Collaboration Guidelines
- **Feature Branches**: Keep main branches stable.  
- **Pull Requests**: Code reviews are mandatory.  
- **Commit Messages**: Descriptive (“Fix X bug in date/time validation”), not “Fix stuff.”  
- **Documentation**: Keep `README.md` up to date, including environment setup steps.

---

## 15. Lessons Learned & Best Practices

1. **Custom Field Implementation**  
   - Default validators for less chance of forgetting.  
   - Keep your constructor flexible to avoid TypeErrors.

2. **Dependency Management**  
   - Test for missing packages before you run your main test suite (a single missing `pytest` can ruin your day).  
   - Document installation steps thoroughly.

3. **Circular Imports**  
   - Create dedicated modules for utilities, or use lazy imports.  
   - If you’re messing with your import statements too often, refactor.

4. **Property Implementation**  
   - `@property` first, then `@<property>.setter`.  
   - Validate in the setter if needed; store in a private attribute.

5. **Error Handling**  
   - Keep all messages in `app/constants.py`. Avoid the dreaded “string mismatch” in tests.  
   - Provide enough context in logs to debug quickly.

6. **Testing**  
   - Edge cases for date/time (lookin’ at you, leap years).  
   - Use mocking (like `freezegun`) for deterministic time-based tests.

---

## 16. Key Takeaways for the Next Coding Session

1. **Validation Logic**  
   - Confirm data types before applying validation.  
   - Centralize error messages, stay consistent.

2. **Testing**  
   - More edge-case coverage.  
   - Keep a good variety of unit, integration, and E2E tests.

3. **Error Handling & Logging**  
   - Don’t just “print” stuff—log it with context.  
   - Make error messages user-friendly (or at least developer-friendly).

4. **Code Organization**  
   - Keep modules small and logical.  
   - Use base classes and utilities to avoid duplication.

---

**End of Document**