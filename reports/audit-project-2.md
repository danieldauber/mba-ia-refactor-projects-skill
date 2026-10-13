================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js) + Express 4.18.2
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 3 | HIGH: 4 | MEDIUM: 3 | LOW: 3

## Findings

### [CRITICAL] Hardcoded Credentials and Live API Keys in Source
File: src/utils.js:1-7
Description: `config` object hardcodes `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_1234567890abcdef"`, and `smtpUser` directly in source. The `pk_live_` prefix indicates an active production payment gateway key.
Impact: Any developer or attacker with repository access has production credentials; secrets committed to git are permanent and irrevocable.
Recommendation: Remove all literals from `config`; read from environment variables via `process.env.PAYMENT_GATEWAY_KEY`, `process.env.DB_PASS`, etc., and document required vars in a `.env.example` file.

### [CRITICAL] Plaintext Password Seed Data and Insecure Storage
File: src/AppManager.js:18
Description: Seed data inserts user `leonan@fullcycle.com.br` with `pass = '123'` — a plaintext password. The `badCrypto` function in `utils.js:17-23` is used for new user creation and is not a real hash (it base64-encodes then truncates to 10 chars), providing no meaningful password protection.
Impact: A database dump or any SQL read exposes every user's actual password; `badCrypto` output is deterministic and trivially reversible.
Recommendation: Replace `badCrypto` with `bcrypt.hash`/`bcrypt.compare` (npm `bcrypt` or `bcryptjs`); update seed data to store a properly hashed password.

### [CRITICAL] No Authentication/Authorization on Admin and Destructive Endpoints
File: src/AppManager.js:80-137
Description: `GET /api/admin/financial-report` (line 80) and `DELETE /api/users/:id` (line 131) have zero authentication checks — no token, session, or middleware validation before executing sensitive operations.
Impact: Any unauthenticated caller can retrieve full financial data or delete any user record.
Recommendation: Implement an auth middleware that validates a JWT or API key and apply it to all `/api/admin/*` and destructive routes.

### [HIGH] N+1 Query Problem in Financial Report
File: src/AppManager.js:83-128
Description: For each course, a query fetches all enrollments; then for each enrollment, two further queries fetch user and payment data individually — producing O(courses × enrollments × 2) database round-trips via nested async callbacks.
Impact: With N courses and M enrollments each, this issues 1 + N + N×M×2 queries; response time degrades exponentially with data volume.
Recommendation: Replace nested queries with a single JOIN: `SELECT c.title, u.name, u.email, p.amount, p.status FROM courses c LEFT JOIN enrollments e ON e.course_id = c.id LEFT JOIN users u ON u.id = e.user_id LEFT JOIN payments p ON p.enrollment_id = e.id` and aggregate in JavaScript.

### [HIGH] God Object / Business Logic in a Single Class with No Layer Separation
File: src/AppManager.js:1-141
Description: `AppManager` merges database initialization, route registration, payment processing logic, enrollment logic, and audit logging into one class. There are no separate model, controller, or service layers.
Impact: Any change to a business rule requires modifying the same file as the DB schema; untestable in isolation; high coupling makes future changes risky.
Recommendation: Decompose into `models/` (data access), `controllers/` (business logic), `routes/` (HTTP layer), and `services/` (payment, notifications) per the MVC guidelines.

### [HIGH] Global Mutable State (Cache and Revenue Counter)
File: src/utils.js:9-10
Description: `globalCache = {}` and `totalRevenue = 0` are module-level mutable objects shared across all requests. `logAndCache` mutates `globalCache` on every checkout.
Impact: State bleeds between requests in a multi-request environment; no isolation between concurrent users; cache grows unboundedly without eviction.
Recommendation: Remove global mutable state; use request-scoped data, a proper caching layer (Redis), or pass state explicitly through function parameters.

### [HIGH] Broken/Insecure Password Hashing Function
File: src/utils.js:17-23
Description: `badCrypto` builds a "hash" by base64-encoding the password 10,000 times and truncating to 10 characters. This is not a cryptographic hash — it is deterministic, collision-prone, and the output space is tiny (base64 charset, 10 chars).
Impact: Stored passwords are trivially reversible; any attacker with DB access can recover plaintext passwords.
Recommendation: Replace with `bcrypt.hash(password, 12)` for storage and `bcrypt.compare(plaintext, hash)` for verification.

### [MEDIUM] Payment Card Number Logged to Console
File: src/AppManager.js:45
Description: `console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`)` logs the full card number and live API key to stdout on every checkout request.
Impact: PCI-DSS violation; card numbers and keys appear in all log aggregation systems, server output, and any log forwarding pipeline.
Recommendation: Remove this log entirely; if tracing is needed, log only the last 4 digits and a masked key reference.

### [MEDIUM] Delete User Without Cascading Cleanup
File: src/AppManager.js:131-137
Description: `DELETE /api/users/:id` deletes a user row but leaves orphaned `enrollments` and `payments` rows. The response message even acknowledges this: `"as matrículas e pagamentos ficaram sujos no banco"`.
Impact: Referential integrity is broken; orphaned payments and enrollments cause incorrect financial reports and potential data leaks.
Recommendation: Use a database transaction to delete related `enrollments` and `payments` before deleting the user, or enable SQLite foreign key enforcement (`PRAGMA foreign_keys = ON`) with `ON DELETE CASCADE`.

### [MEDIUM] Notification / Side-Effect Logic Inline in Route Handler
File: src/AppManager.js:59
Description: `logAndCache(\`last_checkout_${userId}\`, course.title)` performs a side effect (cache write + console log) directly inside the route callback with no abstraction.
Impact: Controller is coupled to caching logic; behavior cannot be changed or tested independently; will grow uncontrolled as more side effects are added.
Recommendation: Extract to a `NotificationService` or `AuditService` module; controller calls `auditService.onCheckout(userId, course)`.

### [LOW] Console Logging Instead of Structured Logger
File: src/AppManager.js:45, src/utils.js:13
Description: `console.log(...)` used throughout for operational logging with no log levels, timestamps, or structured format.
Impact: Logs cannot be filtered by severity; incompatible with log aggregators (ELK, Datadog); no correlation IDs per request.
Recommendation: Replace with a structured logger such as `winston` or `pino`: `logger.info({ userId, courseId }, 'checkout processed')`.

### [LOW] Magic Numbers in Business Logic
File: src/AppManager.js:46
Description: Card brand detection uses the literal `"4"` (`cc.startsWith("4")`) with no named constant or comment explaining this represents a Visa prefix.
Impact: Intent is opaque; changing payment logic requires understanding undocumented numeric conventions.
Recommendation: Extract to a named constant: `const VISA_PREFIX = "4"` or a `PaymentUtils.isVisaCard(cc)` helper.

### [LOW] DEBUG / Development Artifacts Left in Production Path
File: src/app.js:13
Description: `console.log(\`Frankenstein LMS rodando na porta ${config.port}...\`)` uses a debug-style message with informal naming ("Frankenstein") in the production startup path; no environment-aware logging.
Impact: Minor — informal messages in production logs are unprofessional and suggest the codebase has not been hardened for production.
Recommendation: Replace with a structured logger call: `logger.info({ port: config.port }, 'Server started')`.

================================
Total: 13 findings
================================
