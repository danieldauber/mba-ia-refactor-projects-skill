================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~560 lines of code

## Summary
CRITICAL: 4 | HIGH: 3 | MEDIUM: 3 | LOW: 3

## Findings

### [CRITICAL] SQL Injection via String Concatenation
File: models.py:28
Description: `cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))` — pattern is repeated across 14 additional queries in the same file using string concatenation with unsanitized inputs, including email, senha, nome, categoria, and termo fields that come directly from request body and query params.
Impact: Attacker can bypass authentication, exfiltrate all user data including plaintext passwords, drop tables, or execute arbitrary SQL against the SQLite instance.
Recommendation: Replace all string-concatenated queries with parameterized queries using `?` placeholders and tuple arguments (e.g., `cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))`).

### [CRITICAL] Arbitrary SQL Execution Endpoint (No Auth)
File: app.py:59-78
Description: Route `/admin/query` accepts a `sql` field in the JSON body and passes it directly to `cursor.execute(query)` with no authentication, authorization, or input sanitization. Accessible to any HTTP client.
Impact: Any unauthenticated user can read all data, drop all tables, modify any record, or (via SQLite extensions) escalate to OS-level code execution.
Recommendation: Remove the endpoint entirely. Use Alembic or Flask-Migrate for schema management.

### [CRITICAL] Hardcoded SECRET_KEY
File: app.py:7
Description: `app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"` — literal string committed to source control.
Impact: Any developer with repo access or any attacker who reads the code can forge Flask session cookies and impersonate any user, including admins.
Recommendation: Read from environment: `app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")` and raise an error if unset in production.

### [CRITICAL] SECRET_KEY Exposed in API Response
File: controllers.py:289
Description: The `/health` endpoint returns `"secret_key": "minha-chave-super-secreta-123"` in the JSON response body, directly exposing the Flask session signing key to any API client.
Impact: Any caller of `/health` obtains the secret key and can forge authenticated session tokens.
Recommendation: Remove all config values from the health check response. Return only `{"status": "ok", "database": "connected"}`.

### [HIGH] Plaintext Password Storage and Comparison
File: models.py:122-131 (creation), models.py:105-120 (login), database.py:75-83 (seed)
Description: Passwords are inserted into the database as raw strings (`senha = '" + senha + "'"`) and compared directly in SQL. The seed data includes `admin123`, `123456`, and `senha123` in plaintext.
Impact: A database file leak exposes every user's actual password, enabling credential-stuffing attacks against all services where users reuse passwords.
Recommendation: Hash with `werkzeug.security.generate_password_hash` on creation; verify with `check_password_hash` on login. Rehash seed data.

### [HIGH] Business Logic Embedded in the Data Layer
File: models.py:235-273
Description: `relatorio_vendas()` both executes SQL queries AND applies discount business rules (thresholds 10000/5000/1000, rates 0.10/0.05/0.02) in the same function.
Impact: Business rules cannot be tested without a database connection; changing a discount policy requires modifying the data access layer.
Recommendation: Move discount calculation to `controllers/relatorio_controller.py`. Model function should return raw aggregates only.

### [HIGH] N+1 Query Pattern in Order Retrieval
File: models.py:171-233
Description: `get_pedidos_usuario()` and `get_todos_pedidos()` both execute one query per order to fetch items, then one query per item to fetch the product name — using nested `cursor2` and `cursor3` inside loops.
Impact: With 100 orders averaging 5 items each, this generates 601 queries per request instead of 2. Performance degrades linearly with data volume.
Recommendation: Replace with a single JOIN query: `SELECT p.*, ip.*, pr.nome FROM pedidos p LEFT JOIN itens_pedido ip ON ... LEFT JOIN produtos pr ON ...` and group results in Python.

### [MEDIUM] Global Mutable Database Connection
File: database.py:4-10
Description: `db_connection = None` at module level, reused across all requests via `global db_connection`. Flask's development server is single-threaded, masking this issue; production servers (Gunicorn) are multi-threaded.
Impact: Concurrent requests share one SQLite connection, causing `sqlite3.ProgrammingError: Recursive use of cursors not allowed` and data corruption under load.
Recommendation: Use Flask's `g` object with `@app.teardown_appcontext` for per-request connection lifecycle management.

### [MEDIUM] User Passwords Returned in API Responses
File: models.py:79-87 (get_todos_usuarios), models.py:94-103 (get_usuario_por_id)
Description: Both functions include `"senha": row["senha"]` in the returned dict. Any GET to `/usuarios` or `/usuarios/<id>` returns plaintext passwords to the caller.
Impact: Any authenticated (or unauthenticated — no auth middleware exists) client can enumerate all user passwords via `/usuarios`.
Recommendation: Exclude the `senha` field from all serialization functions. Only return `id`, `nome`, `email`, `tipo`, `criado_em`.

### [MEDIUM] Notification Side Effects Inline in Controller
File: controllers.py:208-210
Description: `criar_pedido()` contains `print("ENVIANDO EMAIL/SMS/PUSH: ...")` simulating notification dispatch directly inside the route handler.
Impact: Controller is coupled to notification concerns; switching notification channels requires modifying request-handling code; untestable in isolation.
Recommendation: Extract to `services/notification_service.py`; controller calls `notification_service.on_order_created(pedido_id, usuario_id)`.

### [LOW] Magic Numbers in Discount Logic
File: models.py:257-262
Description: Discount thresholds and rates appear as bare literals: `if faturamento > 10000`, `faturamento * 0.1`, `> 5000`, `* 0.05`, `> 1000`, `* 0.02`.
Impact: Intent is unclear without reading context; changing a rate requires finding all occurrences; risk of inconsistency.
Recommendation: Extract to named constants: `DISCOUNT_THRESHOLD_HIGH = 10000`, `DISCOUNT_RATE_HIGH = 0.10`.

### [LOW] print() Used as Logging Mechanism
File: controllers.py:8, 11, 57, 106, 161, 178-183, 208-210, 219, 248-250
Description: `print(...)` is used throughout controllers for operational logging (request counts, errors, login events, notifications).
Impact: No log levels, no timestamps, no structured format; cannot be routed to log aggregators or filtered by severity in production.
Recommendation: Replace with `import logging; logger = logging.getLogger(__name__)` and `logger.info(...)` / `logger.error(...)`.

### [LOW] DEBUG Mode Hardcoded to True
File: app.py:8
Description: `app.config["DEBUG"] = True` is set unconditionally in source code, and also `app.run(..., debug=True)` at line 88.
Impact: Werkzeug's interactive debugger is enabled in production, allowing any client who triggers an unhandled exception to execute arbitrary Python code via the browser PIN.
Recommendation: `DEBUG = os.environ.get("DEBUG", "false").lower() == "true"` in `config/settings.py`.

================================
Total: 13 findings
================================
