# Reference: MVC Architecture Guidelines

## Target Structure

The refactored project must follow this directory layout:

### Python/Flask

```
src/
├── config/
│   └── settings.py          # All config: SECRET_KEY, DB_PATH, DEBUG, etc.
├── models/
│   ├── __init__.py
│   └── <entity>_model.py    # One file per domain entity (produto, usuario, pedido)
├── controllers/
│   ├── __init__.py
│   └── <entity>_controller.py  # One file per domain entity
├── views/
│   ├── __init__.py
│   └── <entity>_routes.py   # Route definitions using Blueprint, one per entity
├── services/
│   ├── __init__.py
│   └── <service>_service.py # Cross-cutting concerns: notifications, auth, etc.
├── middlewares/
│   └── error_handler.py     # Centralized error handling
└── app.py                   # Composition root — creates app, registers blueprints
database.py                  # DB connection management (kept at root or in config/)
```

### Node.js/Express

```
src/
├── config/
│   └── settings.js          # env vars, constants
├── models/
│   └── <Entity>Model.js     # Data access per entity
├── controllers/
│   └── <entity>Controller.js
├── routes/
│   └── <entity>Routes.js    # Express Router per entity
├── services/
│   └── <entity>Service.js
├── middlewares/
│   └── errorHandler.js
└── app.js                   # Composition root
```

---

## Layer Responsibilities

### Config (`config/settings.py`)
- Reads ALL configuration from environment variables with sensible defaults
- Exports constants used by other layers
- **MUST NOT** import from any other layer
- Example:
  ```python
  import os
  SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
  DB_PATH = os.environ.get("DB_PATH", "app.db")
  DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
  ```

### Models (`models/<entity>_model.py`)
- Responsible ONLY for data access: SELECT, INSERT, UPDATE, DELETE
- Receives validated, typed parameters — does NOT validate input
- Returns plain dicts or None/lists
- **MUST** use parameterized queries — NEVER string concatenation in SQL
- **MUST NOT** contain business logic (discounts, pricing rules, state machines)
- **MUST NOT** import from controllers or views
- Example:
  ```python
  def get_by_id(db, produto_id: int) -> dict | None:
      cursor = db.cursor()
      cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
      row = cursor.fetchone()
      return dict(row) if row else None
  ```

### Controllers (`controllers/<entity>_controller.py`)
- Orchestrates the request: validates input → calls model(s) → applies business logic → returns result dict
- Does NOT import `flask.request` or `flask.jsonify` — receives parsed data as parameters
- Returns plain Python dicts (not HTTP responses)
- Contains business logic (e.g., discount calculation, stock check)
- May call services for side effects (notifications, email)
- Example:
  ```python
  def criar_pedido(db, usuario_id: int, itens: list) -> dict:
      if not itens:
          raise ValueError("Pedido deve ter pelo menos 1 item")
      # business logic here
      pedido_id = pedido_model.insert(db, usuario_id, total)
      return {"pedido_id": pedido_id, "total": total}
  ```

### Views / Routes (`views/<entity>_routes.py`)
- Thin HTTP layer: parse request → call controller → return JSON response
- Handles HTTP concerns: status codes, request parsing, response formatting
- Contains error handling that maps exceptions to HTTP status codes
- Uses Flask Blueprint (Python) or Express Router (Node.js)
- **MUST NOT** contain business logic or SQL
- Example:
  ```python
  from flask import Blueprint, request, jsonify
  from controllers import produto_controller
  from database import get_db

  produtos_bp = Blueprint("produtos", __name__)

  @produtos_bp.route("/produtos", methods=["POST"])
  def criar():
      dados = request.get_json()
      try:
          resultado = produto_controller.criar(get_db(), dados)
          return jsonify({"dados": resultado, "sucesso": True}), 201
      except ValueError as e:
          return jsonify({"erro": str(e)}), 400
  ```

### Services (`services/<service>_service.py`)
- Encapsulates cross-cutting concerns: email, SMS, push notifications, external APIs
- Called by controllers as side effects
- **MUST NOT** import from views or models directly
- Example:
  ```python
  def notify_order_created(pedido_id: int, usuario_id: int):
      # real implementation sends email/SMS; stub logs for now
      import logging
      logger = logging.getLogger(__name__)
      logger.info(f"Order {pedido_id} created for user {usuario_id}")
  ```

### Entry Point (`app.py`)
- Creates the Flask app
- Registers all Blueprints
- Loads config
- Sets up logging
- **No business logic, no route definitions, no SQL**

---

## MVC Rules (Non-Negotiable)

1. SQL queries live ONLY in model files
2. HTTP request/response objects live ONLY in view/route files
3. Business logic lives ONLY in controller or service files
4. Config lives ONLY in config files — no hardcoded values elsewhere
5. Passwords are ALWAYS hashed before storage
6. All SQL uses parameterized queries — no string concatenation
7. No global mutable state for DB connections — use per-request or pooled connections
