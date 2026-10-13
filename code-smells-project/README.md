# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

A aplicação sobe em `http://localhost:5000`. O banco SQLite (`loja.db`) é criado automaticamente no primeiro boot, já com produtos e usuários de exemplo.

---

## Análise Manual

### Projeto: code-smells-project (Python/Flask — API de E-commerce)

#### [CRITICAL] SQL Injection via concatenação de strings
**Arquivo:** `models.py` — múltiplas ocorrências (linhas 28, 48–50, 57–62, 68, 92, 110, 127–130, 140, 155–161, 164–166, 174, 188, 220, 280–297)
**Severidade:** CRITICAL
**Justificativa:** Praticamente todas as queries são construídas com `+` e `str()`, incluindo campos vindos diretamente de parâmetros de rota ou body do request. Um atacante pode injetar SQL arbitrário em qualquer endpoint (busca, login, criação). O login em especial (`email = '...' AND senha = '...'`) é trivialmente contornável via `' OR '1'='1`.

#### [CRITICAL] Endpoint de execução arbitrária de SQL
**Arquivo:** `app.py:59–78`
**Severidade:** CRITICAL
**Justificativa:** O endpoint `/admin/query` aceita um campo `sql` no body e executa diretamente com `cursor.execute(query)`. Sem nenhuma autenticação. Qualquer cliente HTTP pode dropar tabelas, exfiltrar dados ou executar queries destrutivas.

#### [CRITICAL] Secret key hardcoded + exposta na resposta da API
**Arquivo:** `app.py:7` (definição) e `controllers.py:289` (exposição)
**Severidade:** CRITICAL
**Justificativa:** `SECRET_KEY = "minha-chave-super-secreta-123"` está literal no código-fonte e é retornada pela rota `/health` na resposta JSON. Qualquer cliente pode ler a chave e forjar tokens de sessão.

#### [HIGH] Senhas armazenadas em texto puro
**Arquivo:** `models.py:127–130` (criação), `models.py:109–119` (login), `database.py:76–79` (seed)
**Severidade:** HIGH
**Justificativa:** Senhas são inseridas no banco sem hashing (`senha = '" + senha + "'"`). O seed pré-popula o banco com `admin123` e `123456`. Um vazamento do banco expõe credenciais reais de todos os usuários.

#### [HIGH] Lógica de negócio embutida no modelo
**Arquivo:** `models.py:235–273`
**Severidade:** HIGH
**Justificativa:** A função `relatorio_vendas()` executa queries SQL E calcula descontos com regras de negócio (limiares 10000/5000/1000 e taxas 10%/5%/2%). Viola SRP: a camada de dados não deve conter regras de negócio.

#### [HIGH] N+1 queries nos pedidos
**Arquivo:** `models.py:171–233`
**Severidade:** HIGH
**Justificativa:** Para cada pedido, um cursor secundário busca itens; para cada item, um cursor terciário busca o nome do produto. Com N pedidos e M itens, gera N×M+N queries extras. Performance degrada exponencialmente.

#### [MEDIUM] Conexão global mutável ao banco de dados
**Arquivo:** `database.py:4–10`
**Severidade:** MEDIUM
**Justificativa:** `db_connection = None` como variável global e `global db_connection` dentro de `get_db()`. Em servidores multi-thread (Gunicorn/uWSGI), a mesma conexão é compartilhada entre threads simultâneas, causando corrupção de dados e erros de cursor.

#### [MEDIUM] Lógica de notificação embutida no controller
**Arquivo:** `controllers.py:208–210`
**Severidade:** MEDIUM
**Justificativa:** `print("ENVIANDO EMAIL/SMS/PUSH: ...")` dentro de `criar_pedido()`. O controller está acoplado a responsabilidades de notificação. Impossível trocar o canal de notificação sem modificar o controller.

#### [MEDIUM] Senhas retornadas na API de usuários
**Arquivo:** `models.py:79–86` e `models.py:94–103`
**Severidade:** MEDIUM
**Justificativa:** Os campos `"senha": row["senha"]` são incluídos nos dicts retornados por `get_todos_usuarios()` e `get_usuario_por_id()`. Qualquer GET em `/usuarios` expõe senhas (em texto puro) de todos os usuários.

#### [LOW] Magic numbers na lógica de desconto
**Arquivo:** `models.py:257–262`
**Severidade:** LOW
**Justificativa:** Valores `10000`, `5000`, `1000`, `0.1`, `0.05`, `0.02` aparecem sem nomes. A intenção não é clara e alterar um limiar exige encontrar todos os literais espalhados.

#### [LOW] `print()` como mecanismo de log
**Arquivo:** `controllers.py` — múltiplas ocorrências (linhas 8, 11, 57, 106, 161, 178–182, 208–210, 219, 248–250)
**Severidade:** LOW
**Justificativa:** Logs via `print()` não têm nível de severidade, timestamp, nem podem ser roteados para sistemas de observabilidade. Em produção, o output vai para stdout sem estrutura.

#### [LOW] DEBUG habilitado hardcoded
**Arquivo:** `app.py:8`
**Severidade:** LOW
**Justificativa:** `app.config["DEBUG"] = True` está fixo no código. O modo debug do Flask ativa o Werkzeug interactive debugger, que permite execução de código Python arbitrário via browser.
