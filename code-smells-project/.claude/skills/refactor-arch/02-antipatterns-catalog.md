# Reference: Anti-Patterns Catalog

Each entry specifies: severity, detection signals (exact code patterns to search for), and recommended fix.

---

## CRITICAL

### 1. SQL Injection via String Concatenation
**Severity:** CRITICAL  
**Detection signals:**
- `cursor.execute("SELECT * FROM ... WHERE id = " + str(id))`
- `cursor.execute("INSERT INTO ... VALUES ('" + var + "'")`
- Any SQL string built with `+` operator or `%` formatting with user-controlled values
- `query += " AND campo = '" + valor + "'"`

**Impact:** Attackers can read, modify, or delete any data in the database; full system compromise possible.

**Fix:** Use parameterized queries: `cursor.execute("SELECT * FROM t WHERE id = ?", (id,))` (SQLite) or `cursor.execute("SELECT * FROM t WHERE id = %s", (id,))` (PostgreSQL/MySQL).

---

### 2. Hardcoded Credentials / Secrets
**Severity:** CRITICAL  
**Detection signals:**
- `SECRET_KEY = "..."` with a literal string value in source code
- `password = "hardcoded_value"`
- `API_KEY = "sk-..."` or `TOKEN = "..."` with literal values
- Database URLs with embedded credentials: `postgresql://user:pass@host/db`
- Seed data with plaintext admin passwords: `("admin@example.com", "admin123", "admin")`

**Impact:** Any developer or attacker with code access has credentials; secrets committed to git are permanent.

**Fix:** Move to environment variables (`os.environ.get("SECRET_KEY")`) or a `.env` file loaded via `python-dotenv`. Never commit `.env` to git.

---

### 3. Arbitrary Code / SQL Execution Endpoint
**Severity:** CRITICAL  
**Detection signals:**
- Route that accepts a `sql` parameter and passes it directly to `cursor.execute(query)`
- Route named `/admin/query`, `/debug/exec`, `/run`, `/eval`
- `exec(user_input)` or `eval(user_input)` in any route handler

**Impact:** Any caller can read all data, drop tables, or execute OS commands (via SQLite's `load_extension` or similar).

**Fix:** Remove the endpoint entirely. Use database migration tools for schema changes.

---

### 4. Sensitive Data Exposed in API Response
**Severity:** CRITICAL  
**Detection signals:**
- `"senha": row["senha"]` returned in a JSON response
- `"secret_key": app.config["SECRET_KEY"]` in a route handler response
- `"password"` field included in user serialization
- Health check endpoint returning internal config values

**Impact:** Passwords, tokens, and configuration are exposed to any API consumer.

**Fix:** Explicitly exclude sensitive fields from serialization. Never return passwords or secrets in responses.

---

## HIGH

### 5. Plaintext Password Storage
**Severity:** HIGH  
**Detection signals:**
- `INSERT INTO usuarios ... senha = '" + senha + "'"` with no hashing
- `SELECT * FROM usuarios WHERE email = ? AND senha = ?` comparing raw passwords
- `bcrypt` or `hashlib` not imported in files that handle user creation/login

**Impact:** A database leak exposes every user's actual password.

**Fix:** Hash passwords with `werkzeug.security.generate_password_hash` on creation; verify with `check_password_hash` on login.

---

### 6. Business Logic in the Model / Data Layer
**Severity:** HIGH  
**Detection signals:**
- Discount/pricing calculations inside a function that also queries the database
- Validation rules embedded in the same function as `INSERT` or `UPDATE`
- A "model" function returns computed business metrics (e.g., `ticket_medio`, `desconto_aplicavel`)

**Impact:** Logic cannot be tested in isolation; changing a business rule requires modifying database-layer code.

**Fix:** Move business logic to a controller or service layer. Models should only perform CRUD operations.

---

### 7. Global Mutable State for Database Connection
**Severity:** HIGH  
**Detection signals:**
- `db_connection = None` at module level
- `global db_connection` inside a function
- Single connection object reused across requests in a multi-threaded server

**Impact:** Thread-safety issues under concurrent load; a single connection failure breaks all requests.

**Fix:** Use `flask.g` with `@app.teardown_appcontext` to manage per-request connections, or use a connection pool (SQLAlchemy, `psycopg2.pool`).

---

### 8. N+1 Query Problem
**Severity:** HIGH  
**Detection signals:**
- A `cursor.execute(...)` call inside a `for row in rows:` loop
- Multiple nested cursors (`cursor2`, `cursor3`) created inside a loop
- Fetching parent records then fetching each child record individually in a loop

**Impact:** For N orders with M items each, produces N×M+N queries instead of 2; degrades exponentially with data volume.

**Fix:** Use a JOIN query to fetch related data in a single query, or batch-fetch with `WHERE id IN (...)`.

---

## MEDIUM

### 9. No Authentication / Authorization on Protected Endpoints
**Severity:** MEDIUM  
**Detection signals:**
- Admin routes (`/admin/*`) with no `@login_required` or JWT verification decorator
- Routes that delete or reset data with no auth check
- No middleware that validates session tokens or API keys before processing requests

**Impact:** Any unauthenticated user can access admin operations.

**Fix:** Implement an auth middleware/decorator that checks a valid session token or JWT before allowing access to sensitive routes.

---

### 10. Notification / Side-Effect Logic Inside Controllers
**Severity:** MEDIUM  
**Detection signals:**
- `print("ENVIANDO EMAIL: ...")` inside a route handler
- `print("ENVIANDO SMS: ...")` or `print("ENVIANDO PUSH: ...")` simulating notifications
- Direct SMTP calls or Twilio calls inside a controller function

**Impact:** Controller is coupled to notification logic; cannot change notification behavior without modifying controller; untestable in isolation.

**Fix:** Extract to a `NotificationService` class/module. Controller calls `notification_service.send_order_created(order_id)`.

---

### 11. Duplicate Code Across Similar Functions
**Severity:** MEDIUM  
**Detection signals:**
- Two functions with near-identical structure (e.g., `get_todos_pedidos` and `get_pedidos_usuario`) sharing 80%+ of their code
- Same field-mapping dict `{"id": row["id"], "nome": row["nome"], ...}` repeated in multiple functions
- Same validation block copy-pasted across multiple route handlers

**Impact:** Bug fixes or schema changes must be applied in multiple places; inconsistency risk.

**Fix:** Extract shared serialization into a helper function (`serialize_produto(row)`). Extract shared validation into a reusable validator.

---

### 12. Deprecated API Usage
**Severity:** MEDIUM  
**Detection signals:**
- `app.add_url_rule(...)` used instead of `@app.route(...)` decorator (Flask deprecated pattern)
- `sqlite3.connect(...)` with `check_same_thread=False` used in a multi-threaded context without pooling
- `cursor.execute` with `%s` string interpolation (deprecated in favor of parameterized queries)
- Node.js: `require('url').parse(...)` instead of `new URL(...)` (deprecated since Node 11)
- Node.js: `Buffer()` constructor instead of `Buffer.from()` / `Buffer.alloc()` (deprecated since Node 6)

**Impact:** Code may break in future versions; some patterns introduce security risks.

**Fix:** Replace with current equivalents documented in the framework's migration guide.

---

## LOW

### 13. Magic Numbers
**Severity:** LOW  
**Detection signals:**
- Numeric literals in business logic without named constants: `if faturamento > 10000`, `* 0.1`
- HTTP status codes hardcoded without comment: `return ..., 422`
- Timeout values: `time.sleep(30)`

**Impact:** Intent is unclear; changing a threshold requires hunting for all occurrences.

**Fix:** Extract to named constants: `DISCOUNT_THRESHOLD_HIGH = 10000`, `DISCOUNT_RATE_HIGH = 0.10`.

---

### 14. Console Logging Instead of Structured Logger
**Severity:** LOW  
**Detection signals:**
- `print("ERRO: " + str(e))` in production code paths
- `print("Listando " + str(len(items)) + " items")` in route handlers
- No import of `logging` module; no logger configuration

**Impact:** Logs cannot be filtered by level; cannot be sent to log aggregators; no timestamps or severity context.

**Fix:** Replace `print` with `import logging; logger = logging.getLogger(__name__)` and use `logger.info(...)`, `logger.error(...)`.

---

### 15. DEBUG Mode Enabled in Production Config
**Severity:** LOW  
**Detection signals:**
- `app.config["DEBUG"] = True` hardcoded in source
- `app.run(..., debug=True)` hardcoded
- `DEBUG=True` in a committed `.env` file

**Impact:** Flask debug mode enables the interactive debugger which allows arbitrary code execution via the browser.

**Fix:** Read from environment: `app.config["DEBUG"] = os.environ.get("DEBUG", "false").lower() == "true"`.
