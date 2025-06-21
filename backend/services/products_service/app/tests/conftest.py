# Em tests/conftest.py

import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.main import app
from app.core.database import get_session

# CORREÇÃO: Usamos um banco de dados SQLite em memória para os testes.
# Ele é criado do zero a cada execução do pytest e depois some.
DATABASE_URL_TEST = "sqlite:///:memory:"

# O parâmetro 'connect_args' é específico para o SQLite e necessário
# para que ele funcione corretamente com o FastAPI em múltiplas threads.
engine = create_engine(DATABASE_URL_TEST, connect_args={"check_same_thread": False})

@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    # Cria as tabelas antes de cada teste
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    # Apaga as tabelas após cada teste
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    
    yield TestClient(app)
    
    app.dependency_overrides.clear()