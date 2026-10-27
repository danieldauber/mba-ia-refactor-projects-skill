# Criação de Skills — Refatoração Arquitetural Automatizada

Ao longo do curso você aprendeu o que são Skills e como elas permitem que um agente de IA atue como um especialista em tarefas específicas. Agora imagine o seguinte cenário: você herdou 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias.

Neste desafio, você vai criar uma Skill que automatiza esse processo — analisando, auditando e refatorando qualquer projeto para o padrão MVC, independente da tecnologia.

## Objetivo

Você deve entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

## Contexto

### Definição de Severidades

Para padronizar a sua auditoria e os relatórios gerados pela IA, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Tecnologias obrigatórias

- **Ferramenta:** uma das três opções abaixo (não são aceitas outras ferramentas):
  - Claude Code
  - Gemini CLI
  - OpenAI Codex
- **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

> **Nota sobre a ferramenta:** Os exemplos deste documento usam o Claude Code (`.claude/skills/`) como referência, pois é a ferramenta utilizada no curso. Se você optar por Gemini CLI ou Codex, adapte o nome da pasta e o comando de invocação conforme a convenção dela — o conceito de skill e a estrutura interna (SKILL.md + arquivos de referência) permanecem os mesmos.

## Requisitos

### 1. Análise Manual dos Projetos

Antes de criar a skill, você deve entender os problemas que ela vai resolver.

**Tarefas:**

- Analisar o projeto `code-smells-project/` (Python/Flask — API de E-commerce)
- Analisar o projeto `ecommerce-api-legacy/` (Node.js/Express — LMS API com fluxo de checkout)
- Analisar o projeto `task-manager-api/` (Python/Flask — API de Task Manager)

Para cada projeto, identificar e documentar no mínimo 5 problemas, incluindo pelo menos:

- 1 de severidade CRITICAL ou HIGH
- 2 de severidade MEDIUM
- 2 de severidade LOW

Documentar os achados na seção "Análise Manual" do seu `README.md`

> **Dica:** Não precisa encontrar todos os problemas — foque nos que têm maior impacto arquitetural. Use os projetos como insumo para entender quais padrões sua skill precisa detectar.

> **Por que 3 projetos?** Dois são Python/Flask (com níveis de organização diferentes) e um é Node.js/Express. Sua skill precisa funcionar nos 3 para provar que é verdadeiramente agnóstica de tecnologia — lidando tanto com código completamente desestruturado quanto com projetos que já possuem alguma separação de camadas.

### 2. Criação da Skill

Agora que você conhece os problemas, crie uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

**Tarefas:**

Criar a skill dentro do projeto `code-smells-project/` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Criar arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento | O que deve conter |
|---|---|
| Análise de projeto | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade |
| Template de relatório | Formato padronizado do relatório de auditoria (Fase 2) |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração | Padrões concretos de transformação para cada anti-pattern (com exemplos de código) |

> **Nota:** Você tem liberdade para organizar os arquivos de referência como preferir — pode usar os nomes e a quantidade de arquivos que fizer sentido para sua skill. O importante é que todas as 5 áreas de conhecimento estejam cobertas. O nome da skill (`refactor-arch`) e o arquivo `SKILL.md` são obrigatórios e não devem ser alterados. O path da skill segue a convenção da ferramenta escolhida (no Claude Code, por exemplo, é `.claude/skills/refactor-arch/`).

**Requisitos da skill:**

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos, independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

### 3. Execução da Skill

Execute sua skill nos 3 projetos e valide que ela funciona em todas as stacks.

#### Projeto 1 — code-smells-project (Python/Flask)

Invocar a skill no Claude Code:

```bash
claude "/refactor-arch"
```

> **Nota:** O comando acima é o exemplo com Claude Code. Se você estiver usando Gemini CLI ou Codex, utilize o comando equivalente para invocar uma skill na sua ferramenta.

- Verificar que a Fase 1 detecta corretamente a stack e imprime o resumo
- Verificar que a Fase 2 encontra no mínimo 5 dos problemas documentados na sua análise manual
- Confirmar a execução da Fase 3
- Verificar que a Fase 3:
  - Cria a estrutura de diretórios baseada em MVC
  - A aplicação inicia sem erros
  - Os endpoints originais continuam respondendo
- Salvar o relatório de auditoria (output da Fase 2) em `reports/audit-project-1.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

Prove que sua skill é reutilizável em outro projeto de backend, mas com stack diferente.

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `ecommerce-api-legacy/`
- Invocar a skill:

```bash
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

- Verificar que as 3 fases executam corretamente neste projeto
- Salvar o relatório em `reports/audit-project-2.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 3 — task-manager-api (Python/Flask)

Agora o teste com um projeto Python/Flask que já possui alguma organização de camadas (models, routes, services, utils).

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `task-manager-api/`
- Invocar a skill:

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

- Verificar que:
  - A Fase 1 detecta corretamente Python/Flask como stack e identifica o domínio de Task Manager
  - A Fase 2 identifica problemas mesmo em um projeto parcialmente organizado
  - A Fase 3 melhora a estrutura sem quebrar a aplicação (todos os endpoints devem continuar respondendo)
- Salvar o relatório em `reports/audit-project-3.md`
- Commitar o código refatorado do projeto no repositório

> **Nota:** Este projeto já possui alguma separação de camadas, mas isso não significa que a arquitetura está adequada. A skill deve identificar tanto problemas de código (segurança, performance, qualidade) quanto oportunidades de melhoria arquitetural. Se houver mudanças estruturais necessárias, a skill deve propô-las e executá-las.

#### Validação

Para cada projeto refatorado, valide o seguinte checklist:

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> **Dica:** Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Entregável

Repositório público no GitHub (fork do repositório base) contendo:

- Skill completa em `.claude/skills/refactor-arch/` (dentro dos 3 projetos)
- Código refatorado dos 3 projetos (resultado da execução da Fase 3, commitado no repositório)
- Relatórios de auditoria em `reports/` (3 arquivos)
- `README.md` atualizado

### Estrutura do repositório

Faça um fork do repositório base contendo os três projetos com code smells.

> **Nota:** A estrutura abaixo usa Claude Code como exemplo (`.claude/skills/`). Se estiver usando outra ferramenta, adapte os caminhos conforme a convenção dela.

```
desafio-skills/
├── README.md                              # Sua documentação
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (API de E-commerce)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← SUA SKILL AQUI
│   │           ├── SKILL.md
│   │           └── (arquivos de referência)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API com checkout)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── src/
│   │   ├── app.js
│   │   ├── AppManager.js
│   │   └── utils.js
│   ├── api.http
│   └── package.json
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (API de Task Manager)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
└── reports/                               # Relatórios gerados
    ├── audit-project-1.md                 # Saída da Fase 2 no projeto 1
    ├── audit-project-2.md                 # Saída da Fase 2 no projeto 2
    └── audit-project-3.md                 # Saída da Fase 2 no projeto 3
```

**O que você vai criar:**

- `.claude/skills/refactor-arch/` — A skill completa (SKILL.md + arquivos de referência)
- Código refatorado dos 3 projetos — resultado da execução da Fase 3, commitado no repositório
- `reports/audit-project-{1,2,3}.md` — Relatório de auditoria de cada projeto
- `README.md` — Documentação do seu processo

**O que já vem pronto:**

- `code-smells-project/` — API de E-commerce Python/Flask com code smells intencionais
- `ecommerce-api-legacy/` — LMS API Node.js/Express (com fluxo de checkout) e problemas de implementação
- `task-manager-api/` — API de Task Manager Python/Flask com organização parcial e problemas de segurança/qualidade

> **Dica:** Cada projeto contém problemas intencionais de diferentes severidades (CRITICAL, HIGH, MEDIUM, LOW), incluindo falhas de segurança, violações arquiteturais e problemas de qualidade de código. Parte do desafio é identificá-los por conta própria através da análise manual do código.

### README.md deve conter

**A) Seção "Análise Manual":**

- Lista dos problemas identificados manualmente em cada projeto
- Classificação por severidade
- Justificativa de por que cada problema é relevante

**B) Seção "Construção da Skill":**

- Decisões de design: como estruturou o SKILL.md e os arquivos de referência
- Quais anti-patterns incluiu no catálogo e por quê
- Como garantiu que a skill é agnóstica de tecnologia
- Desafios encontrados e como resolveu

**C) Seção "Resultados":**

- Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
- Comparação antes/depois da estrutura de cada projeto
- Checklist de validação preenchido para cada projeto
- Screenshots ou logs mostrando as aplicações rodando após refatoração
- Observações sobre como a skill se comportou em stacks diferentes

**D) Seção "Como Executar":**

- Pré-requisitos (a ferramenta escolhida — Claude Code, Gemini CLI ou Codex — instalada e configurada)
- Comandos para executar a skill em cada projeto
- Como validar que a refatoração funcionou

### Ordem de execução sugerida

**1. Analisar os projetos manualmente**

Leia o código dos três projetos e documente os problemas encontrados.

**2. Criar a skill**

Escreva o SKILL.md e os arquivos de referência.

**3. Executar nos 3 projetos**

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-{1,2,3}.md`.

**4. Iterar**

Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Critérios de Aceite

A skill deve atingir os seguintes mínimos em **todos os 3 projetos**:

| Critério | Requisito |
|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | OBRIGATÓRIO (3/3 projetos) |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO (3/3 projetos) |

**IMPORTANTE:** Todos os critérios devem ser atingidos nos 3 projetos, não apenas em um!

> **Sobre o projeto 3 (task-manager-api):** Este projeto já possui alguma organização. "aplicação funciona" significa que a API inicia sem erros e todos os endpoints continuam respondendo corretamente.

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills) — Documentação oficial sobre como criar e estruturar Skills
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview) — Visão geral do Claude Code e suas capacidades
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Guia completo da Anthropic sobre construção de Skills
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) — Blog oficial da Anthropic sobre Agent Skills

---

## Análise Manual

### Projeto 1 — code-smells-project (Python/Flask — E-commerce API)

| Severidade | Arquivo | Problema |
|---|---|---|
| CRITICAL | `app.py:7` | `SECRET_KEY` hardcoded como literal no código-fonte; qualquer acesso ao repositório permite forjar cookies de sessão. |
| CRITICAL | `app.py:59-78` | Endpoint `/admin/query` executa SQL arbitrário recebido no body sem autenticação — qualquer cliente HTTP pode dropar tabelas ou exfiltrar dados. |
| CRITICAL | `models.py:28` | 15+ queries constroem SQL por concatenação de string com entradas do request — SQL Injection clássico. |
| CRITICAL | `controllers.py:289` | Endpoint `/health` retorna `secret_key` no body JSON, expondo a chave de sessão para qualquer chamador. |
| HIGH | `models.py:122-131` | Senhas armazenadas e comparadas em plaintext no banco; seed inclui `admin123` e `123456` em texto puro. |
| HIGH | `models.py:235-273` | Regras de desconto (thresholds e taxas) misturadas com queries SQL na mesma função da camada de dados. |
| HIGH | `models.py:171-233` | N+1 query: consulta uma query por pedido e outra por item dentro de loops aninhados — 601 queries para 100 pedidos de 5 itens. |
| MEDIUM | `database.py:4-10` | Conexão SQLite global mutável (`global db_connection`) compartilhada entre requisições — corrupção de dados sob carga concorrente. |
| MEDIUM | `models.py:79-87` | Funções de listagem de usuários incluem campo `senha` (plaintext) na resposta — qualquer cliente pode enumerar todas as senhas. |
| MEDIUM | `controllers.py:208-210` | Lógica de notificação (`print("ENVIANDO EMAIL...")`) inline dentro do handler de rota — acoplamento de responsabilidades. |
| LOW | `models.py:257-262` | Magic numbers nos thresholds de desconto (`10000`, `5000`, `1000`, `0.10`, `0.05`, `0.02`) sem constantes nomeadas. |
| LOW | `controllers.py` (múltiplas) | `print()` usado como logger em toda a camada de controle — sem níveis, timestamps ou roteamento para agregadores. |
| LOW | `app.py:8` | `DEBUG = True` hardcoded — debugger interativo do Werkzeug habilitado em produção, permitindo execução de código arbitrário. |

### Projeto 2 — ecommerce-api-legacy (Node.js/Express — LMS API)

| Severidade | Arquivo | Problema |
|---|---|---|
| CRITICAL | `src/utils.js:1-7` | `dbPass`, `paymentGatewayKey` (prefixo `pk_live_` — chave de produção ativa) e `smtpUser` hardcoded como literais no objeto `config`. |
| CRITICAL | `src/AppManager.js:18` | Seed insere senha `'123'` em plaintext; `badCrypto` (base64 × 10k, truncado em 10 chars) não é hash criptográfico — reversível trivialmente. |
| CRITICAL | `src/AppManager.js:80-137` | `GET /api/admin/financial-report` e `DELETE /api/users/:id` sem qualquer verificação de autenticação ou autorização. |
| HIGH | `src/AppManager.js:83-128` | N+1 exponencial: para cada curso → query de matrículas; para cada matrícula → 2 queries (usuário + pagamento) em callbacks aninhados. |
| HIGH | `src/AppManager.js:1-141` | God Object: `AppManager` unifica inicialização do banco, registro de rotas, lógica de pagamento, matrículas e audit log em uma única classe. |
| HIGH | `src/utils.js:9-10` | `globalCache = {}` e `totalRevenue = 0` mutáveis no escopo de módulo — estado vaza entre requisições concorrentes; cache sem eviction. |
| HIGH | `src/utils.js:17-23` | `badCrypto` não é hash: base64 × 10.000 truncado em 10 chars — espaço de saída mínimo, determinístico, facilmente revertido. |
| MEDIUM | `src/AppManager.js:45` | Número do cartão (`cc`) e chave de API (`config.paymentGatewayKey`) logados em `console.log` — violação PCI-DSS. |
| MEDIUM | `src/AppManager.js:131-137` | DELETE de usuário não remove `enrollments` nem `payments` relacionados — integridade referencial quebrada, relatórios financeiros corrompidos. |
| MEDIUM | `src/AppManager.js:59` | Side effect de cache inline dentro do handler de rota — sem abstração, sem testabilidade. |
| LOW | `src/AppManager.js`, `src/utils.js` | `console.log` como mecanismo de logging sem níveis, timestamps ou formato estruturado. |
| LOW | `src/AppManager.js:46` | Magic string `"4"` para detectar bandeira Visa sem constante nomeada nem comentário explicativo. |
| LOW | `src/app.js:13` | Mensagem de startup com nome informal ("Frankenstein") no caminho de produção — ausência de logging orientado a ambiente. |

### Projeto 3 — task-manager-api (Python/Flask — Task Manager)

| Severidade | Arquivo | Problema |
|---|---|---|
| CRITICAL | `app.py:13` | `SECRET_KEY = 'super-secret-key-123'` hardcoded — tokens JWT/sessão podem ser forjados por qualquer pessoa com acesso ao repositório. |
| CRITICAL | `services/notification_service.py:9-10` | `self.email_password = 'senha123'` e `taskmanager@gmail.com` hardcoded no construtor — credenciais SMTP comprometidas permanentemente. |
| CRITICAL | `models/user.py:16-25` | `User.to_dict()` inclui `'password': self.password` — hash da senha retornado em toda resposta de usuário. |
| HIGH | `models/user.py:28-32` | `hashlib.md5(pwd.encode()).hexdigest()` — MD5 sem salt e sem work factor; rainbow tables quebram em segundos. |
| HIGH | `routes/` (3 arquivos) | Lógica de detecção de overdue e validação de status duplicada verbatim em `task_routes.py`, `user_routes.py` e `report_routes.py`. |
| HIGH | `routes/report_routes.py:53-68` | N+1: `User.query.all()` seguido de `Task.query.filter_by(user_id=u.id)` dentro de loop — 1 + N queries por requisição. |
| MEDIUM | Todas as rotas | Nenhum endpoint tem autenticação; `/login` retorna `'fake-jwt-token-' + str(user.id)` nunca validado. |
| MEDIUM | `routes/report_routes.py:157-223` | CRUD de categorias registrado dentro do blueprint de relatórios — violação de single responsibility. |
| MEDIUM | `routes/task_routes.py:18-28` | Serialização manual de task inline mesmo existindo `Task.to_dict()` — dois caminhos de serialização divergentes. |
| MEDIUM | `app.py:34` | `debug=True` hardcoded — debugger interativo Werkzeug ativo em produção. |
| LOW | Múltiplos arquivos | `print()` em vez de `logging` em rotas e no serviço de notificação. |
| LOW | `app.py:7` | `import os, sys, json, datetime` — apenas `datetime` é utilizado; mesma redundância em `task_routes.py` e `utils/helpers.py`. |
| LOW | `routes/user_routes.py:210` | Token fake `'fake-jwt-token-' + str(user.id)` preditível e nunca validado em nenhum endpoint. |

---

## Construção da Skill

### Estrutura do SKILL.md

O `SKILL.md` define três fases sequenciais obrigatórias com comportamento explicitamente imperativo — cada fase tem uma pré-condição (a anterior deve ter concluído) e uma condição de parada (erro não passa em silêncio). A Fase 2 tem um hard stop: a skill imprime o relatório completo e aguarda `y`/`yes` antes de modificar qualquer arquivo. A Fase 3 valida boot + endpoints antes de declarar sucesso.

### Arquivos de referência

| Arquivo | Conteúdo |
|---|---|
| `01-project-analysis.md` | Heurísticas de detecção: extensão de arquivo → linguagem, `requirements.txt`/`package.json` → framework e versão, schema SQLite/SQL → tabelas, contagem de imports → domínio. |
| `02-antipatterns-catalog.md` | 15 anti-patterns com sinais de detecção linha-a-linha, severidade e recomendação. Inclui detecção de APIs deprecated (MD5 → bcrypt, `print` → `logging`, `cursor.execute(string)` → queries parametrizadas). |
| `03-report-template.md` | Template de relatório com header padronizado, seção de summary (contagem por severidade) e bloco por finding com campos: severidade, arquivo:linha, descrição, impacto, recomendação. |
| `04-mvc-guidelines.md` | Estrutura-alvo MVC: `src/config/`, `src/models/`, `src/controllers/`, `src/views/`, `src/services/`, `src/middlewares/` — com responsabilidades definidas por camada e regras de dependência (views não acessam models diretamente). |
| `05-refactoring-playbook.md` | 12 padrões Python + 3 padrões Node.js com exemplos antes/depois: SECRET_KEY → env var, SQL concatenado → parametrizado, MD5 → bcrypt, `print` → `logging`, lógica inline → service, serialização inline → `to_dict()`, global mutable state → request-scoped, N+1 raw SQL → JOIN, endpoint arbitrário → remoção, regra de negócio duplicada → service compartilhado, N+1 ORM → `outerjoin+group_by`, error handling centralizado, `badCrypto` → `bcrypt.hash`, `Buffer()` deprecated → `Buffer.from()`, `url.parse` deprecated → `new URL()`, `app.get` monolítico → Express Router por entidade. |

### Anti-patterns incluídos no catálogo e por quê

A seleção partiu dos três projetos analisados manualmente: cada anti-pattern foi incluído porque aparece em pelo menos um dos projetos reais. A distribuição por severidade reflete o impacto observado:

| Severidade | Anti-patterns | Critério de inclusão |
|---|---|---|
| **CRITICAL (4)** | SQL Injection, credenciais hardcoded, endpoint de execução arbitrária, dados sensíveis em resposta | Exploráveis remotamente sem autenticação; impacto imediato de confidencialidade ou integridade. Todos os três projetos tinham pelo menos um desses. |
| **HIGH (4)** | Senha em plaintext/hash fraco, regra de negócio na camada errada, God Object/God Class, estado global mutável | Comprometem segurança ou arquitetura de forma que impede testes e manutenção; exigem refatoração estrutural significativa. |
| **MEDIUM (4)** | N+1 query, falta de autenticação em rotas, lógica duplicada entre controllers, DEBUG hardcoded | Degradam performance ou qualidade mas não são exploráveis diretamente; detectáveis sem execução. |
| **LOW (3)** | `print()` em vez de logging, imports não utilizados, magic numbers/strings | Problemas de legibilidade e manutenibilidade; baixo risco imediato mas acumulam dívida técnica. |
| **Deprecated APIs** | MD5 (`hashlib.md5`), `Buffer()` constructor, `url.parse`, `console.log` como logger | Incluídos porque os três projetos usavam APIs obsoletas como substitute de segurança real (`badCrypto`, MD5) — a detecção dessas é o primeiro passo para descobrir o problema de segurança subjacente. |

### Agnóstica de tecnologia

A agnósia de tecnologia foi garantida por três decisões de design:

1. A Fase 1 detecta stack dinamicamente (lê `requirements.txt`, `package.json`, extensões de arquivo) e passa essa informação como contexto para as fases seguintes — a skill não assume Python nem Node.
2. O catálogo de anti-patterns cobre padrões que existem em ambas as stacks (credenciais hardcoded, N+1, God Object, falta de autenticação) com sinais de detecção específicos por linguagem quando necessário.
3. O playbook de refatoração inclui exemplos antes/depois para Python e JavaScript nos padrões que diferem entre as duas linguagens.

### Desafios e soluções

- **Projeto 3 já tinha camadas parciais:** A skill precisava detectar que `models/`, `routes/`, `services/` existiam mas ainda tinham problemas internos. Solução: a Fase 1 mapeia a arquitetura atual explicitamente e a Fase 2 audita o conteúdo dos arquivos, não apenas sua existência.
- **Remoção de legados após migração:** Na primeira execução, a Fase 3 criou o `src/` mas não removeu os arquivos originais. Solução: o SKILL.md foi atualizado com uma etapa explícita de remoção de legados com critérios precisos (arquivo totalmente migrado + validação aprovada) e atualização obrigatória do README com o novo entry point.

---

## Resultados

### Resumo dos relatórios de auditoria

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---|---|---|---|
| code-smells-project | 4 | 3 | 3 | 3 | 13 |
| ecommerce-api-legacy | 3 | 4 | 3 | 3 | 13 |
| task-manager-api | 3 | 3 | 4 | 3 | 13 |

### Comparação antes/depois

#### code-smells-project

| Antes | Depois |
|---|---|
| 4 arquivos monolíticos (~560 linhas) | `src/` com config, models, controllers, views, services, middlewares |
| SQL Injection por concatenação | Queries parametrizadas com `?` placeholders |
| SECRET_KEY e DEBUG hardcoded | Lidos de variáveis de ambiente via `config/settings.py` |
| Senhas em plaintext | `werkzeug.security.generate_password_hash` (bcrypt) |
| Endpoint `/admin/query` executando SQL arbitrário | Endpoint removido |
| `print()` como logger | `logging.getLogger(__name__)` por módulo |

#### ecommerce-api-legacy

| Antes | Depois |
|---|---|
| 3 arquivos (God Object `AppManager`) | `src/` com models, controllers, routes, services |
| Chave de pagamento `pk_live_` e senha SMTP hardcoded | Lidas de `process.env` com `.env.example` documentado |
| `badCrypto` (base64 truncado) | `bcrypt.hash` / `bcrypt.compare` |
| N+1 exponencial em relatório financeiro | JOIN único com agregação em JavaScript |
| Número de cartão logado em plaintext | Log removido; apenas últimos 4 dígitos registrados |
| Estado global mutável (`globalCache`, `totalRevenue`) | Request-scoped; cache isolado por requisição |

#### task-manager-api

| Antes | Depois |
|---|---|
| `app.py` + `models/` + `routes/` + `services/` + `utils/` na raiz | `src/` com config, models, controllers, views, services, middlewares |
| `SECRET_KEY = 'super-secret-key-123'` hardcoded | `os.environ.get('SECRET_KEY')` em `src/config/settings.py` |
| MD5 sem salt para senhas | `werkzeug.security.generate_password_hash` (scrypt/bcrypt) |
| `User.to_dict()` retornava campo `password` | Campo `password` removido de `to_dict()` |
| Credenciais SMTP hardcoded em `NotificationService.__init__` | Lidas de env vars; stub automático se `SMTP_USER` vazio |
| `print()` em rotas e serviços | `logging.getLogger(__name__)` por módulo |
| Lógica de overdue duplicada em 3 arquivos | Centralizada em `services/task_service.py` |

### Checklist de validação

#### Projeto 1 — code-smells-project

**Fase 1 — Análise**
- [x] Linguagem detectada: Python
- [x] Framework detectado: Flask
- [x] Domínio: E-commerce API (produtos, pedidos, usuários)
- [x] 4 arquivos analisados

**Fase 2 — Auditoria**
- [x] Relatório segue o template definido
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade
- [x] 13 findings identificados (≥ 5)
- [x] Detecção de APIs deprecated incluída (MD5, `print`, queries concatenadas)
- [x] Skill pausou e pediu confirmação antes da Fase 3

**Fase 3 — Refatoração**
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para `config/settings.py` (sem hardcoded)
- [x] Models criados por domínio
- [x] Views/Routes separadas
- [x] Controllers concentram o fluxo
- [x] Error handling centralizado em middleware
- [x] Entry point claro: `src/app.py`
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente

#### Projeto 2 — ecommerce-api-legacy

**Fase 1 — Análise**
- [x] Linguagem detectada: JavaScript (Node.js)
- [x] Framework detectado: Express 4.18.2
- [x] Domínio: LMS API com fluxo de checkout
- [x] 3 arquivos analisados

**Fase 2 — Auditoria**
- [x] Relatório segue o template definido
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade
- [x] 13 findings identificados (≥ 5)
- [x] Detecção de APIs deprecated incluída (`badCrypto`, `console.log`)
- [x] Skill pausou e pediu confirmação antes da Fase 3

**Fase 3 — Refatoração**
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config (sem hardcoded)
- [x] Models criados para abstrair dados
- [x] Routes separadas por domínio
- [x] Controllers concentram o fluxo
- [x] Error handling centralizado
- [x] Entry point claro: `src/app.js`
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente

#### Projeto 3 — task-manager-api

**Fase 1 — Análise**
- [x] Linguagem detectada: Python
- [x] Framework detectado: Flask 3.0.0
- [x] Domínio: Task Manager API
- [x] 11 arquivos analisados

**Fase 2 — Auditoria**
- [x] Relatório segue o template definido
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade
- [x] 13 findings identificados (≥ 5)
- [x] Detecção de APIs deprecated incluída (MD5, `print`)
- [x] Skill pausou e pediu confirmação antes da Fase 3

**Fase 3 — Refatoração**
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para `src/config/settings.py`
- [x] Models migrados para `src/models/`
- [x] Views/Routes separadas em `src/views/`
- [x] Controllers criados em `src/controllers/`
- [x] Error handling centralizado em `src/middlewares/error_handler.py`
- [x] Entry point claro: `python src/app.py`
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente
- [x] Arquivos legados removidos (`app.py`, `models/`, `routes/`, `services/`, `utils/`, `database.py` da raiz)

---

### Logs de execução após refatoração

#### code-smells-project

```
$ PYTHONPATH=. python app.py
==================================================
SERVIDOR INICIADO
Rodando em http://localhost:5000
==================================================
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://127.0.0.1:5000

$ curl http://localhost:5000/health
{"counts":{"pedidos":1,"produtos":11,"usuarios":3},"database":"connected","status":"ok","versao":"1.0.0"}
# HTTP 200 ✓

$ curl http://localhost:5000/produtos
{"dados":[...],"sucesso":true}
# HTTP 200 ✓

$ curl http://localhost:5000/usuarios
{"dados":[...],"sucesso":true}
# HTTP 200 ✓
```

#### ecommerce-api-legacy

```
$ node src/app.js
{"level":"info","message":{"port":3000},"timestamp":"2026-10-27T23:28:30.683Z"}

$ curl -X POST http://localhost:3000/api/checkout \
    -H "Content-Type: application/json" \
    -d '{"userId":1}'
{"error":"Missing required fields: name, email, courseId, cardNumber"}
# HTTP 400 ✓ (validação funcionando, endpoint acessível)

$ curl http://localhost:3000/api/admin/financial-report
{"error":"Unauthorized"}
# HTTP 401 ✓ (auth middleware protegendo rota sensível)

$ curl -X DELETE http://localhost:3000/api/users/1
{"error":"Unauthorized"}
# HTTP 401 ✓ (auth middleware protegendo rota destrutiva)
```

#### task-manager-api

```
$ python seed.py
Seed concluído com sucesso!
  3 usuários
  4 categorias
  10 tasks

$ PYTHONPATH=. python src/app.py
 * Serving Flask app 'app'
 * Debug mode: off
 * Running on http://127.0.0.1:5000

$ curl http://localhost:5000/health
{"status":"ok","timestamp":"2026-10-27 20:15:29.271628"}
# HTTP 200 ✓

$ curl http://localhost:5000/tasks
[{...}, {...}, ...]
# HTTP 200, 10 tasks ✓

$ curl http://localhost:5000/users
[{...}, {...}, {...}]
# HTTP 200, 3 users (sem campo password) ✓

$ curl http://localhost:5000/reports/summary
{"user_productivity":[...3 rows...],"overdue":{"count":2,...},...}
# HTTP 200, user_productivity via single outerjoin query ✓
```

### Observações sobre comportamento da skill em stacks diferentes

**code-smells-project (Python/Flask monolítico):** A Fase 1 identificou corretamente os 4 arquivos e a arquitetura "monolítica" porque todos os imports relevantes estavam concentrados em `models.py` e `controllers.py`. A Fase 3 teve o trabalho mais extenso aqui — precisou decompor um único arquivo de ~350 linhas em 4 camadas MVC distintas. O risco de quebrar funcionalidade era alto; a skill resolveu mantendo a lógica de negócio de desconto no controller e criando models puros que só fazem acesso a dados.

**ecommerce-api-legacy (Node.js/Express):** A única stack JavaScript do conjunto. A Fase 1 adaptou corretamente os sinais de detecção (`package.json` → Express 4.18.2, arquivos `.js`, ausência de `requirements.txt`). A Fase 3 gerou código Node.js idiomático — `require`/`module.exports`, `async/await`, `bcrypt` em vez de `werkzeug`, estrutura de pastas `routes/` em vez de `views/`. O `badCrypto` não tinha equivalente nos projetos Python; a skill o identificou como uma variant local do padrão "hash fraco" graças ao sinal de detecção textual no catálogo (`base64`, loop de 10k iterações).

**task-manager-api (Python/Flask parcialmente organizado):** O projeto mais interessante para a skill. A Fase 1 não podia simplesmente contar arquivos e dizer "monolítico" — havia `models/`, `routes/`, `services/` separados. A skill reconheceu a arquitetura como "parcialmente organizada com problemas internos" e a Fase 2 focou no conteúdo dos arquivos em vez da estrutura de diretórios. A Fase 3 foi a mais cirúrgica: não recriou a estrutura do zero mas elevou cada camada — extraindo `is_overdue` para um service compartilhado, substituindo o N+1 por `outerjoin+group_by`, removendo `password` do `to_dict()`.

---

## Como Executar

### Pré-requisitos

- **Claude Code** instalado e configurado (`claude --version` deve responder)
- Python 3.9+ e `pip` para os projetos Python/Flask
- Node.js 18+ e `npm` para o projeto Node.js/Express

### Executar a skill em cada projeto

```bash
# Projeto 1 — code-smells-project (Python/Flask)
cd code-smells-project
claude "/refactor-arch"

# Projeto 2 — ecommerce-api-legacy (Node.js/Express)
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3 — task-manager-api (Python/Flask)
cd ../task-manager-api
claude "/refactor-arch"
```

A skill pausa após a Fase 2 para revisão do relatório. Digite `y` para confirmar a refatoração (Fase 3).

### Validar a refatoração

#### code-smells-project

```bash
cd code-smells-project
pip install -r requirements.txt
PYTHONPATH=. python app.py
# Em outro terminal:
curl http://localhost:5000/health
curl http://localhost:5000/produtos
```

#### ecommerce-api-legacy

```bash
cd ecommerce-api-legacy
npm install
node src/app.js
# Em outro terminal:
curl http://localhost:3000/api/courses
```

#### task-manager-api

```bash
cd task-manager-api
pip install -r requirements.txt
python seed.py       # popula o banco com dados de exemplo
python src/app.py
# Em outro terminal:
curl http://localhost:5000/health
curl http://localhost:5000/tasks
curl http://localhost:5000/users
```

### Relatórios de auditoria

Os relatórios gerados pela Fase 2 estão em:

```
reports/
├── audit-project-1.md   # code-smells-project
├── audit-project-2.md   # ecommerce-api-legacy
└── audit-project-3.md   # task-manager-api
```

---

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.