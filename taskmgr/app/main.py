from fastapi import FastAPI
from app.models.db import create_db_and_tables
from app.api.v1 import health, users, projects, tasks, tags, attachments
from app.core.logging_config import logger  # 👈 novo import

app = FastAPI(title="Task Manager API")


@app.on_event("startup")
def on_startup():
    logger.info("API iniciada (startup)")  # 👈 log de inicialização
    create_db_and_tables()


@app.on_event("shutdown")
def on_shutdown():
    logger.info("API finalizada (shutdown)")  # 👈 log ao encerrar


app.include_router(health.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(tags.router, prefix="/api/v1")
app.include_router(attachments.router, prefix="/api/v1")
