# Reference: Project Analysis Heuristics

## Language Detection

| Signal | Language |
|---|---|
| `requirements.txt`, `*.py`, `setup.py`, `pyproject.toml` | Python |
| `package.json`, `*.js`, `*.ts`, `*.mjs` | Node.js |
| `pom.xml`, `build.gradle`, `*.java` | Java |
| `go.mod`, `*.go` | Go |
| `Gemfile`, `*.rb` | Ruby |

## Framework Detection

### Python
| Signal | Framework |
|---|---|
| `from flask import` or `import flask` in source files | Flask |
| `from django` or `import django` | Django |
| `from fastapi import` | FastAPI |
| `uvicorn` in requirements.txt | FastAPI/Starlette |

To get framework version: read `requirements.txt` or run `pip show flask`.

### Node.js
| Signal | Framework |
|---|---|
| `require('express')` or `import express` | Express |
| `require('fastify')` | Fastify |
| `require('koa')` | Koa |
| `@nestjs/core` in package.json | NestJS |

To get framework version: read `package.json` `dependencies` field.

## Dependency Extraction

- **Python:** read `requirements.txt`, strip version pins, list package names
- **Node.js:** read `package.json`, extract `dependencies` and `devDependencies` keys

## Domain Detection

Read all route definitions and function/method names. Identify domain entities by looking at:
- Route paths (e.g., `/produtos`, `/orders`, `/users`)
- Table names in SQL queries (`FROM produtos`, `FROM pedidos`)
- Model class names or function names (`get_todos_produtos`, `createOrder`)

Describe the domain in one sentence: what the application does and its main entities.

## Architecture Detection

### Monolithic (single file)
- All routes, DB access, and business logic in one file
- Signal: one large `app.py` or `app.js` with 200+ lines and multiple concerns

### Flat (multiple files, no clear layers)
- Files exist but without clear MVC separation
- Signal: `models.py` contains both data access AND business logic; `controllers.py` imports `database` directly

### Partial MVC
- Some layer separation exists but incomplete
- Signal: `models/`, `routes/`, `services/` directories exist but controllers or config layer is missing

### MVC
- Clear separation into Models, Views/Routes, Controllers, and Config
- Entry point only composes the app

## File Mapping

List all `.py` or `.js`/`.ts` files (excluding `__pycache__`, `node_modules`, `.git`).

For each file, note:
- Number of lines
- Primary concern (routing, data access, business logic, config, utilities)

## Database Schema Detection

### Python/SQLite
Look for `CREATE TABLE` statements in any `.py` file or `.sql` file.

### Python/SQLAlchemy
Look for classes inheriting from `Base` or `db.Model`.

### Node.js/Sequelize
Look for `sequelize.define(` or `DataTypes` usage.

### Node.js/Mongoose
Look for `new Schema({` or `mongoose.model(`.

List all detected table/collection names.
