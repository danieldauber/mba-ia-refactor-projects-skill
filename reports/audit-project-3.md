================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0
Files:   11 analyzed | ~1160 lines of code

## Summary
CRITICAL: 3 | HIGH: 3 | MEDIUM: 4 | LOW: 3

## Findings

### [CRITICAL] Hardcoded Secret Key in Application Config
File: app.py:13
Description: `app.config['SECRET_KEY'] = 'super-secret-key-123'` is a literal string committed directly in source code.
Impact: Any developer or attacker with repository access has the secret key; JWT/session tokens can be forged.
Recommendation: Replace with `os.environ.get('SECRET_KEY')` and load from a `.env` file via `python-dotenv`.

### [CRITICAL] Hardcoded SMTP Credentials in Service
File: services/notification_service.py:9-10
Description: `self.email_password = 'senha123'` is a literal plaintext password inside the `NotificationService.__init__` method; the email user `taskmanager@gmail.com` is also hardcoded.
Impact: Anyone with code access has working email credentials; credentials committed to git are permanently exposed even after removal.
Recommendation: Read credentials from environment variables: `os.environ.get('SMTP_USER')` and `os.environ.get('SMTP_PASSWORD')`.

### [CRITICAL] Sensitive Data Exposed in API Response (Password Field)
File: models/user.py:16-25
Description: `User.to_dict()` includes `'password': self.password` in its return value; this dict is returned directly in `user_routes.py:86`, `user_routes.py:130`, `user_routes.py:207-210`, and `report_routes.py:139-143`.
Impact: Every API call that returns a user object (GET /users, POST /users, PUT /users, GET /login) leaks the hashed password to the caller.
Recommendation: Remove the `password` field from `User.to_dict()` and never return it in any response.

### [HIGH] Weak Password Hashing (MD5)
File: models/user.py:28-32
Description: `User.set_password` and `User.check_password` use `hashlib.md5(pwd.encode()).hexdigest()` to hash passwords; MD5 is a fast, non-salted hash with no work factor.
Impact: A database leak allows full password recovery via rainbow tables or brute-force within seconds; minimum password length of 4 characters (`user_routes.py:64`) compounds the exposure.
Recommendation: Replace with `werkzeug.security.generate_password_hash` (bcrypt/scrypt) on creation and `check_password_hash` on verification.

### [HIGH] Business Logic and Validation Duplicated Across Route Files
File: routes/task_routes.py:30-39, routes/user_routes.py:170-180, routes/report_routes.py:33-43
Description: The overdue-detection logic (`if t.due_date < datetime.utcnow() and t.status not in ['done','cancelled']`) is copy-pasted verbatim across `task_routes.py`, `user_routes.py`, and `report_routes.py`. The same status validation (`['pending','in_progress','done','cancelled']`) is also duplicated in `task_routes.py:110`, `task_routes.py:177`, and `utils/helpers.py:75`.
Impact: Fixing a business rule (e.g., adding a new terminal status) requires locating and updating at least 6 separate sites; inconsistency risk on each update.
Recommendation: Extract `is_overdue(task)` and status/priority validators into a `TaskService` or `services/task_service.py`; routes should delegate to the service layer.

### [HIGH] N+1 Query Problem in Report and User Endpoints
File: routes/report_routes.py:53-68, routes/user_routes.py:13-25
Description: `summary_report()` fetches all users with `User.query.all()` then issues `Task.query.filter_by(user_id=u.id).all()` inside a `for u in users` loop — one extra query per user. `get_users()` calls `len(u.tasks)` per user inside a loop, triggering a lazy-load query per user.
Impact: For N users the endpoint issues N+1 database queries; performance degrades linearly with user count.
Recommendation: Use `db.session.query(User, func.count(Task.id)).outerjoin(Task).group_by(User.id).all()` to fetch user task counts in a single query; or configure `lazy='subquery'` / `lazy='joined'` on the `tasks` relationship.

### [MEDIUM] No Authentication or Authorization on Any Endpoint
File: routes/task_routes.py:11, routes/user_routes.py:10, routes/report_routes.py:12
Description: All routes (including DELETE /users/<id>, DELETE /tasks/<id>, POST /users, GET /reports/summary) have no auth decorator or token validation. The `/login` endpoint generates a `'fake-jwt-token-' + str(user.id)` (user_routes.py:210) that is never validated anywhere.
Impact: Any unauthenticated caller can delete users, create admin accounts, or read all productivity reports.
Recommendation: Implement a `@require_auth` decorator that validates a real JWT (use `flask-jwt-extended`) and apply it to all non-public endpoints.

### [MEDIUM] Category CRUD Endpoints Registered Under `report_bp` Blueprint
File: routes/report_routes.py:157-223
Description: `GET /categories`, `POST /categories`, `PUT /categories/<id>`, and `DELETE /categories/<id>` are registered inside the `report_bp` Blueprint, mixing category resource management with reporting concerns in the same file.
Impact: Violates single-responsibility principle; adding category features requires modifying the reports file; naming is misleading to any future developer.
Recommendation: Create `routes/category_routes.py` with a dedicated `category_bp` Blueprint and move all category routes there.

### [MEDIUM] Duplicate Field-Mapping / Serialization Code in Route Handlers
File: routes/task_routes.py:18-28, routes/user_routes.py:162-169
Description: `get_tasks()` manually builds a `task_data` dict field-by-field (lines 18–28) even though `Task.to_dict()` exists and does the same thing; `get_user_tasks()` in `user_routes.py` repeats the same pattern with a subset of fields.
Impact: Two code paths for task serialization; a schema change (e.g., adding a field) requires updating both `Task.to_dict()` and the inline dict in `get_tasks()`.
Recommendation: Remove the inline dict-building in `get_tasks()` and `get_user_tasks()`; call `t.to_dict()` uniformly.

### [MEDIUM] DEBUG Mode Hardcoded to True
File: app.py:34
Description: `app.run(debug=True, host='0.0.0.0', port=5000)` has `debug=True` as a literal value.
Impact: Flask debug mode enables the Werkzeug interactive debugger, allowing arbitrary Python code execution in the browser if an exception is triggered.
Recommendation: Replace with `app.run(debug=os.environ.get('DEBUG', 'false').lower() == 'true', ...)`.

### [LOW] Console Print Statements Used Instead of Structured Logger
File: routes/task_routes.py:149,153,218,233, routes/user_routes.py:83,89,147, services/notification_service.py:21,24
Description: Route handlers and the notification service use `print(f"Task criada: ...")`, `print(f"ERRO: ...")`, etc. throughout; no `logging` module is configured anywhere in the project.
Impact: Log output cannot be filtered by severity level, routed to log aggregators, or suppressed in tests.
Recommendation: Replace all `print` calls with `import logging; logger = logging.getLogger(__name__)` and use `logger.info` / `logger.error` appropriately.

### [LOW] Unused Imports Across Multiple Files
File: app.py:7, routes/task_routes.py:7, routes/user_routes.py:6, utils/helpers.py:3-7
Description: `app.py` imports `os, sys, json, datetime` but uses only `datetime`; `task_routes.py` imports `json, os, sys, time` with none used; `user_routes.py` imports `json` unused; `utils/helpers.py` imports `os, json, sys, math` with none used.
Impact: Increases cognitive load; `sys` and `os` imports in routes can indicate dead code or abandoned features.
Recommendation: Remove all unused imports.

### [LOW] Fake JWT Token Returned by Login Endpoint
File: routes/user_routes.py:210
Description: The login endpoint returns `'token': 'fake-jwt-token-' + str(user.id)` — a predictable, unverifiable string that provides no actual security.
Impact: Any caller that reads the response can construct a valid-looking token for any user_id; the token is never validated by any endpoint.
Recommendation: Implement real JWT generation using `flask-jwt-extended` (`create_access_token`) and add token validation to protected routes.

================================
Total: 13 findings
================================
