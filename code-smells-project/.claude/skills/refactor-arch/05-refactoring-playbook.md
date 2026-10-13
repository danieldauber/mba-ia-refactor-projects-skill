# Reference: Refactoring Playbook

Each pattern shows a BEFORE (anti-pattern) and AFTER (clean code) transformation.

---

## Pattern 1: SQL Injection → Parameterized Queries

**Applies to:** Anti-pattern #1

**BEFORE:**
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))

cursor.execute(
    "INSERT INTO produtos (nome, preco) VALUES ('" + nome + "', " + str(preco) + ")"
)

query = "SELECT * FROM produtos WHERE 1=1"
if termo:
    query += " AND nome LIKE '%" + termo + "%'"
cursor.execute(query)
```

**AFTER:**
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))

cursor.execute(
    "INSERT INTO produtos (nome, preco) VALUES (?, ?)",
    (nome, preco)
)

query = "SELECT * FROM produtos WHERE 1=1"
params = []
if termo:
    query += " AND nome LIKE ?"
    params.append(f"%{termo}%")
cursor.execute(query, params)
```

---

## Pattern 2: Hardcoded Secrets → Environment Variables

**Applies to:** Anti-pattern #2

**BEFORE:**
```python
# app.py
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
```

**AFTER:**
```python
# config/settings.py
import os
SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

# app.py
from config.settings import SECRET_KEY, DEBUG
app.config["SECRET_KEY"] = SECRET_KEY
app.config["DEBUG"] = DEBUG
```

---

## Pattern 3: Remove Arbitrary Execution Endpoints

**Applies to:** Anti-pattern #3

**BEFORE:**
```python
@app.route("/admin/query", methods=["POST"])
def executar_query():
    dados = request.get_json()
    query = dados.get("sql", "")
    cursor.execute(query)  # executes ANY SQL from the request body
    ...
```

**AFTER:**
```python
# Remove the route entirely.
# For database management, use Flask-Migrate or Alembic:
# flask db upgrade
```

---

## Pattern 4: Passwords → Hashed Storage

**Applies to:** Anti-pattern #5

**BEFORE:**
```python
# Creating user — stores raw password
cursor.execute(
    "INSERT INTO usuarios (email, senha) VALUES (?, ?)",
    (email, senha)
)

# Login — compares raw passwords
cursor.execute(
    "SELECT * FROM usuarios WHERE email = ? AND senha = ?",
    (email, senha)
)
```

**AFTER:**
```python
from werkzeug.security import generate_password_hash, check_password_hash

# Creating user
hashed = generate_password_hash(senha)
cursor.execute(
    "INSERT INTO usuarios (email, senha) VALUES (?, ?)",
    (email, hashed)
)

# Login
cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
row = cursor.fetchone()
if row and check_password_hash(row["senha"], senha):
    return {"id": row["id"], "nome": row["nome"]}
return None
```

---

## Pattern 5: Business Logic Out of Models

**Applies to:** Anti-pattern #6

**BEFORE:**
```python
# models.py — mixes data access with business rules
def relatorio_vendas():
    cursor.execute("SELECT SUM(total) FROM pedidos")
    faturamento = cursor.fetchone()[0] or 0
    # Business logic embedded in model:
    desconto = 0
    if faturamento > 10000:
        desconto = faturamento * 0.1
    elif faturamento > 5000:
        desconto = faturamento * 0.05
    return {"faturamento": faturamento, "desconto": desconto}
```

**AFTER:**
```python
# models/pedido_model.py — only data access
def get_faturamento_bruto(db) -> float:
    cursor = db.cursor()
    cursor.execute("SELECT COALESCE(SUM(total), 0) FROM pedidos")
    return cursor.fetchone()[0]

# controllers/relatorio_controller.py — business logic
DISCOUNT_THRESHOLD_HIGH = 10000
DISCOUNT_RATE_HIGH = 0.10
DISCOUNT_THRESHOLD_MID = 5000
DISCOUNT_RATE_MID = 0.05

def calcular_relatorio_vendas(db) -> dict:
    faturamento = pedido_model.get_faturamento_bruto(db)
    desconto = 0
    if faturamento > DISCOUNT_THRESHOLD_HIGH:
        desconto = faturamento * DISCOUNT_RATE_HIGH
    elif faturamento > DISCOUNT_THRESHOLD_MID:
        desconto = faturamento * DISCOUNT_RATE_MID
    return {
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
    }
```

---

## Pattern 6: Global DB Connection → Per-Request Connection

**Applies to:** Anti-pattern #7

**BEFORE:**
```python
# database.py
db_connection = None

def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect("loja.db", check_same_thread=False)
    return db_connection
```

**AFTER (Flask with g):**
```python
# database.py
import sqlite3
from flask import g
from config.settings import DB_PATH

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontext(close_db)
```

---

## Pattern 7: N+1 Queries → Single JOIN

**Applies to:** Anti-pattern #8

**BEFORE:**
```python
cursor.execute("SELECT * FROM pedidos")
rows = cursor.fetchall()
for row in rows:
    cursor2 = db.cursor()
    cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
    itens = cursor2.fetchall()
    for item in itens:
        cursor3 = db.cursor()
        cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
```

**AFTER:**
```python
cursor.execute("""
    SELECT
        p.id, p.usuario_id, p.status, p.total, p.criado_em,
        ip.produto_id, ip.quantidade, ip.preco_unitario,
        pr.nome AS produto_nome
    FROM pedidos p
    LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = ip.produto_id
    ORDER BY p.id
""")
rows = cursor.fetchall()
# Group by pedido_id in Python
pedidos = {}
for row in rows:
    pid = row["id"]
    if pid not in pedidos:
        pedidos[pid] = {
            "id": pid, "usuario_id": row["usuario_id"],
            "status": row["status"], "total": row["total"],
            "criado_em": row["criado_em"], "itens": []
        }
    if row["produto_id"]:
        pedidos[pid]["itens"].append({
            "produto_id": row["produto_id"],
            "produto_nome": row["produto_nome"],
            "quantidade": row["quantidade"],
            "preco_unitario": row["preco_unitario"]
        })
return list(pedidos.values())
```

---

## Pattern 8: Inline Notifications → Service Layer

**Applies to:** Anti-pattern #10

**BEFORE:**
```python
# controllers.py
def criar_pedido():
    resultado = models.criar_pedido(usuario_id, itens)
    print("ENVIANDO EMAIL: Pedido " + str(resultado["pedido_id"]) + " criado")
    print("ENVIANDO SMS: Seu pedido foi recebido!")
    return jsonify(resultado), 201
```

**AFTER:**
```python
# services/notification_service.py
import logging
logger = logging.getLogger(__name__)

def on_order_created(pedido_id: int, usuario_id: int):
    logger.info(f"[EMAIL] Order {pedido_id} created for user {usuario_id}")
    logger.info(f"[SMS] Order received confirmation for user {usuario_id}")

# controllers/pedido_controller.py
from services import notification_service

def criar_pedido(db, usuario_id, itens):
    resultado = pedido_model.insert(db, usuario_id, itens)
    notification_service.on_order_created(resultado["pedido_id"], usuario_id)
    return resultado
```

---

## Pattern 9: Duplicate Serialization → Helper Function

**Applies to:** Anti-pattern #11

**BEFORE:**
```python
# Repeated in 3 different functions
result.append({
    "id": row["id"],
    "nome": row["nome"],
    "descricao": row["descricao"],
    "preco": row["preco"],
    "estoque": row["estoque"],
    "categoria": row["categoria"],
    "ativo": row["ativo"],
    "criado_em": row["criado_em"]
})
```

**AFTER:**
```python
# models/produto_model.py
def _serialize(row) -> dict:
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": bool(row["ativo"]),
        "criado_em": row["criado_em"]
    }

def get_all(db) -> list:
    cursor = db.cursor()
    cursor.execute("SELECT * FROM produtos")
    return [_serialize(row) for row in cursor.fetchall()]

def get_by_id(db, produto_id: int) -> dict | None:
    cursor = db.cursor()
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
    row = cursor.fetchone()
    return _serialize(row) if row else None
```

---

## Pattern 10: Centralized Error Handling

**Applies to:** General improvement — eliminates try/except duplication in every route

**BEFORE:**
```python
# Every route repeats this pattern:
def listar_produtos():
    try:
        produtos = models.get_todos_produtos()
        return jsonify({"dados": produtos}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
```

**AFTER:**
```python
# middlewares/error_handler.py
from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"erro": "Recurso não encontrado"}), 404

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"erro": str(e.description)}), 400

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"erro": "Erro interno do servidor"}), 500

# views/produto_routes.py — routes are clean
@produtos_bp.route("/produtos", methods=["GET"])
def listar():
    produtos = produto_controller.listar_todos(get_db())
    return jsonify({"dados": produtos, "sucesso": True}), 200
```

---

## Node.js Specific Patterns

### Pattern N1: Deprecated Buffer Constructor → Buffer.from()

**BEFORE:**
```javascript
const buf = new Buffer(data);          // deprecated since Node 6
const buf2 = new Buffer(size);         // deprecated
```

**AFTER:**
```javascript
const buf = Buffer.from(data);
const buf2 = Buffer.alloc(size);
```

### Pattern N2: Deprecated url.parse → new URL()

**BEFORE:**
```javascript
const url = require('url');
const parsed = url.parse(req.url);     // deprecated since Node 11
```

**AFTER:**
```javascript
const parsed = new URL(req.url, `http://${req.headers.host}`);
```

### Pattern N3: Express Router per Entity

**BEFORE:**
```javascript
// app.js — all routes in one file
app.get('/products', (req, res) => { ... });
app.post('/products', (req, res) => { ... });
app.get('/users', (req, res) => { ... });
```

**AFTER:**
```javascript
// routes/productRoutes.js
const router = require('express').Router();
router.get('/', productController.getAll);
router.post('/', productController.create);
module.exports = router;

// app.js
const productRoutes = require('./routes/productRoutes');
app.use('/products', productRoutes);
```
