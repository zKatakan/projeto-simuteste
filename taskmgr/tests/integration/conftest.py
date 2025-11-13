# tests/integration/conftest.py

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

from app.main import app
from app.models.db import get_session  # se o nome/arquivo forem diferentes, ajuste aqui
from app.models import entities  # importa os modelos para registrar as tabelas (não remover)


# Usamos um banco SQLite separado só para os testes de integração
TEST_DB_URL = "sqlite:///./test_integration.db"

engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
)


def _reset_database() -> None:
    """Dropa e recria todas as tabelas no banco de teste."""
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def get_test_session():
    """Session que será injetada na aplicação durante os testes."""
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="session", autouse=True)
def setup_app():
    """
    Sobrescreve a dependência de sessão para usar o banco de teste
    durante toda a sessão de testes.
    """
    _reset_database()
    app.dependency_overrides[get_session] = get_test_session
    yield
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def client(setup_app):
    """
    Entrega um TestClient com o banco zerado em cada teste.
    """
    _reset_database()
    with TestClient(app) as c:
        yield c
