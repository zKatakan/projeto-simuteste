# Task Manager — Simulação e Teste

API REST em FastAPI + SQLite para cumprir os requisitos do projeto (CRUDs, regras de negócio, filtros/ordenação, exceptions, logging, config externa, I/O de arquivos) e a bateria de testes (unit, integração, funcionais, cobertura ≥80%).

## Como rodar
```bash
python -m venv .venv
pip install -r requirements.txt
# Windows: .venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Endpoints
- `POST /api/v1/users`
- `POST /api/v1/projects` | `GET /api/v1/projects/{id}/progress` | `GET /api/v1/projects/{id}/can-archive`
- `POST /api/v1/tags`
- `POST /api/v1/tasks` | `GET /api/v1/tasks` | `PATCH /api/v1/tasks/{id}/status`
- `POST /api/v1/attachments`
- `GET /api/v1/health`

## Testes
```bash
pytest -q
pytest --cov=app --cov-report=term-missing --cov-report=html
# abrir htmlcov/index.html

```
