import os
from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

# Garante que a pasta de dados exista
os.makedirs("./data", exist_ok=True)

# Engine único da aplicação
engine = create_engine(settings.DATABASE_URL, echo=False)


def create_db_and_tables():
    """Cria todas as tabelas mapeadas pelo SQLModel."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Dependência de sessão de banco para FastAPI e testes.

    Uso normal (FastAPI):
        Depends(get_session)

    Nos testes de integração, essa função é sobrescrita no dependency_overrides
    para apontar para um banco de teste em memória.
    """
    with Session(engine) as session:
        yield session
