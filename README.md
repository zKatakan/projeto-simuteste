# Task Manager API – Projeto de Simulação e Teste

## 1. Resumo do projeto

Este projeto é uma **API de Gerenciamento de Tarefas** construída com **FastAPI** e **SQLModel/SQLite**. 

### Funcionalidades principais da API

- CRUD de **usuários, projetos, tarefas, tags, anexos**.
- Regras de negócio de tarefas:
  - Não permitir *due_date* no passado.
  - Limite de tarefas abertas por usuário (`MAX_OPEN_TASKS_PER_USER`).
  - Não permitir concluir (`DONE`) uma tarefa sem responsável.
- Regra de projetos:
  - Projeto só pode ser arquivado se **não tiver tarefas críticas abertas** (prioridade alta e não concluídas).
- Cálculo de **progresso do projeto** com base em tarefas concluídas.

---

## 2. Estrutura do repositório

```text
taskmgr/
├── app/
│   ├── api/v1/          # Rotas da API (tasks, projects, users, etc.)
│   ├── core/            # Configurações, logging, dependências
│   ├── models/          # Entidades (SQLModel) e esquemas (Pydantic)
│   ├── repositories/    # Camada de acesso a dados (Repository/DAO)
│   └── services/        # Regras de negócio (TaskService, ProjectService, etc.)
├── tests/
│   ├── unit/            # Testes unitários (services, repos, validações)
│   ├── integration/     # Testes de integração com banco e fluxo completo
│   ├── functional/      # Testes funcionais de API (httpx + pytest-asyncio)
│   └── functional_black_box/  # Testes funcionais caixa‑preta (services via dublês)
├── pyproject.toml       # Configuração de pytest e coverage
└── README.md            # Este arquivo
```

---

## 3. Como preparar o ambiente

### 3.1. Criar e ativar a virtualenv

**Windows (PowerShell / CMD):**

```bash
python -m venv .venv
.venv\Scripts\activate
```

(O prompt deve ficar com prefixo `(.venv)`.)


---

## 4. Como iniciar a API (opcional para demonstração)

```bash
uvicorn app.main:app --reload
```

- Documentação interativa: <http://127.0.0.1:8000/docs>

---


## 5. Roteiro rápido para apresentação (testes)
* CRIAR USUARIO:
```
{
  "name": "João Silva",
  "email": "joao@example.com"
}
```

* CRIAR PROJETO:
```
{
  "name": "Projeto TCC",
  "description": "Sistema de Gerenciamento de Tarefas"
}

```

* CRIAR TAREFA:
```
{
  "title": "Implementar API",
  "description": "Criar endpoints base",
  "priority": 2,
  "project_id": 1,
  "assignee_id": 1,
  "tag_ids": []
}

```
* REGRA DE NEGÓCIO 1 – Não pode concluir tarefa sem responsável:

Exemplo tentando concluir tarefa sem assignee:

```
{
  "title": "Sem responsável",
  "description": "Teste",
  "priority": 3,
  "project_id": 1,
  "assignee_id": null,
  "tag_ids": []
}

```
PATCH:

```
PATCH /api/v1/tasks/2/status?new_status=DONE

```
Resposta esperada (erro 422):

```
{
  "detail": {
    "code": "no_assignee",
    "message": "Tarefa não pode ser concluída sem responsável."
  }
}

```
* REGRA DE NEGÓCIO 2 – Limite de tarefas abertas por usuário

CRIA TAREFA 
```
{
  "title": "Primeira tarefa",
  "priority": 3,
  "project_id": 1,
  "assignee_id": 1,
  "tag_ids": []
}

```

CRIA SEGUNDA TAREFA PRO MESMO USUARIO:

```
{
  "title": "Segunda tarefa",
  "priority": 3,
  "project_id": 1,
  "assignee_id": 1,
  "tag_ids": []
}

```
Resposta esperada:

```
{
  "detail": {
    "code": "user_overload",
    "message": "Usuário já possui 1 tarefas abertas (limite 1)."
  }
}

```
* Alterar Status da Tarefa (funcionamento fixado com sucesso)

```
{
  "id": 1,
  "status": "DONE"
}

```

* Listar Tarefas com Filtros

```
[
  {
    "id": 1,
    "title": "Implementar API",
    "description": "Criar endpoints base",
    "status": "OPEN",
    "priority": 2,
    "project_id": 1,
    "assignee_id": 1,
    "tags": []
  }
]

```

* Upload de Anexo
```
{
  "filename": "documento.pdf",
  "url": "/api/v1/attachments/documento.pdf"
}

```

### 5.1. Executar **todos** os testes automatizados

Na raiz do projeto (`taskmgr/`), com a virtualenv ativa:

```bash
pytest -v
```

Saída esperada (resumida):
- **62 passed** (todos os testes passaram)
- Alguns *warnings* de depreciação do FastAPI (`on_event`), que podem ser ignorados.

Isso cobre:

- Testes **unitários** (`tests/unit`)
- Testes de **integração** (`tests/integration`)
- Testes **funcionais de API** (`tests/functional`)
- Testes **funcionais caixa‑preta** (`tests/functional_black_box`)

Você pode rodar separadamente, se quiser mostrar por tipo:

```bash
pytest tests/unit -v
pytest tests/integration -v
pytest tests/functional -v
pytest tests/functional_black_box -v
```

### 5.2. Verificar logs da aplicação

Os logs estão configurados em `app/core/logging_config.py` e gravam em `./logs/app.log`.


1. Rode um conjunto de testes (por exemplo `pytest tests/integration -v`).
2. Abra o arquivo:

   ```bash
   notepad logs\app.log
   ```

3. Mostre entradas como:
   - `API iniciada (startup)` / `API finalizada (shutdown)`
   - `Criando tarefa: ...`
   - `User overload: usuário id=... já possui ... tarefas abertas (limite=...)`
   - `Verificando se projeto id=... pode ser arquivado`



---

## 6. Testes estruturais – Cobertura de código (Caixa‑Branca)

A configuração do **coverage** já está no `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["app"]
branch = true

[tool.coverage.report]
show_missing = true
```

### 6.1. Geração de relatório de cobertura (versão simples)

Se o pacote `pytest-cov` estiver instalado:

```bash
pytest --cov=app --cov-report=html
```

Isso vai gerar uma pasta:

```text
htmlcov/
└── index.html
```

Abra o arquivo no navegador:

```bash
start htmlcov\index.html
```

### 6.2. Alternativa usando só `coverage` (caso `pytest-cov` não esteja instalado)

```bash
coverage run -m pytest
coverage html
start htmlcov\index.html
```

---

## 7. Tipos de testes e onde eles estão

### 7.1. Testes Unitários (Caixa‑Branca)

- Pasta: `tests/unit`
- Exemplos:
  - `test_task_service.py`
    - Testa regras de negócio de tarefas:
      - `due_date` no passado → lança `ValidationError`.
      - Limite de tarefas abertas por usuário → lança `DomainError`.
  - `test_project_service.py`
    - Testa `ProjectService.can_archive` com tarefas simuladas.
  - `test_validations.py`
    - Testa validações de entrada e regras específicas.

Com isso, possui:

- **Mínimo de 30 testes unitários** (o projeto tem bem mais).  
- Casos **normais, extremos e de erro**.  
- Uso de **fixtures e parametrização** (principalmente em unit e integration).

### 7.2. Testes de Integração

- Pasta: `tests/integration`
- Exemplos:
  - `test_db_integration.py`
    - Verifica criação de entidades no banco e relacionamentos básicos.
  - `test_task_flow.py`
    - Fluxo completo: criar usuário, projeto, tarefa, atualizar status etc.
  - `test_api_integration.py`
    - Faz chamadas reais na API (via `TestClient`) exercitando regras:
      - Não concluir tarefa sem responsável (status 422).
      - Limite de tarefas por usuário (status 400).
      - Cálculo de progresso do projeto (0%, 50%, 100%).



### 7.3. Testes Funcionais (Caixa‑Preta)

- Pasta: `tests/functional`
- Uso de **`httpx.AsyncClient` + `pytest-asyncio`**, sem olhar a implementação interna.
- Validam:
  - Endpoints com diferentes métodos HTTP (GET, POST, PATCH).
  - Status codes e respostas JSON.
  - Cenários de aceitação das principais regras de negócio.

- Pasta: `tests/functional_black_box`
  - Testes de `TaskService` e `ProjectService` usando *dublês* (`FakeTaskRepo`, `FakeProjectRepo`).
  - Focam em **entradas x saídas**; tratam os services como caixa‑preta.


### 7.4. Testes específicos por tipo

- **Testes de API/REST**
  - `tests/functional/test_api_projects.py`
  - `tests/functional/test_api_tasks.py`
  - `tests/integration/test_api_integration.py`
  - Usam `httpx.AsyncClient` ou `TestClient` para chamar rotas reais.

- **Testes de Exceções**
  - `tests/unit/test_task_service.py`
  - `tests/unit/test_validations.py`
  - Validam lançamento de `DomainError`, `ValidationError` e mensagens específicas.

- **Testes com Mocks/Stubs**
  - `tests/functional_black_box/helpers.py`
    - Define `DummyTask`, `FakeTaskRepo`, `FakeProjectRepo` para isolar banco/infra.
  - Testes em `tests/functional_black_box/*.py` usam esses dublês.

---


