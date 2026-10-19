# task-manager-api

API de Task Manager em Python/Flask usada como entrada do desafio `refactor-arch`. Projeto refatorado pela skill para o padrão MVC, com remoção das vulnerabilidades de segurança identificadas na Fase 2 (SECRET_KEY hardcoded, hash MD5, senha exposta em resposta, credenciais SMTP hardcoded).

## Estrutura pós-refatoração

```
task-manager-api/
├── src/
│   ├── app.py                  # entry point (composition root)
│   ├── database.py
│   ├── config/
│   │   └── settings.py         # configuração via variáveis de ambiente
│   ├── models/
│   │   ├── category_model.py
│   │   ├── task_model.py
│   │   └── user_model.py       # bcrypt em vez de MD5; password fora do to_dict
│   ├── controllers/
│   │   ├── category_controller.py
│   │   ├── report_controller.py
│   │   ├── task_controller.py
│   │   └── user_controller.py
│   ├── views/
│   │   ├── category_routes.py
│   │   ├── report_routes.py
│   │   ├── task_routes.py
│   │   └── user_routes.py
│   ├── services/
│   │   └── notification_service.py  # credenciais via env vars
│   └── middlewares/
│       └── error_handler.py
├── seed.py
└── requirements.txt
```

## Como rodar

```bash
pip install -r requirements.txt
python seed.py
python src/app.py
```

A aplicação sobe em `http://localhost:5000`. O `seed.py` popula o banco SQLite (`tasks.db`) com usuários, categorias e tasks de exemplo — **rode-o antes do primeiro boot**.

## Variáveis de ambiente (opcionais)

| Variável | Padrão | Descrição |
|---|---|---|
| `SECRET_KEY` | `change-me-in-production` | Chave de sessão Flask |
| `DATABASE_URI` | `sqlite:///tasks.db` | URI do banco |
| `DEBUG` | `false` | Modo debug |
| `SMTP_HOST` | `smtp.gmail.com` | Host SMTP |
| `SMTP_PORT` | `587` | Porta SMTP |
| `SMTP_USER` | _(vazio)_ | Usuário SMTP — se vazio, emails são logados como stub |
| `SMTP_PASSWORD` | _(vazio)_ | Senha SMTP |
