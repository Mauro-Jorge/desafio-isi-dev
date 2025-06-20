from fastapi import FastAPI
from sqlmodel import SQLModel

# ANTES: from app.core.database import engine
# DEPOIS (CORRETO):
from core.database import engine
from api.routes import products

def create_db_and_tables():
    """Cria as tabelas no banco de dados se elas não existirem."""
    SQLModel.metadata.create_all(engine)

app = FastAPI(
    title="Products Service",
    on_startup=[create_db_and_tables],
)

app.include_router(products.router, prefix="/api/v1")

@app.get("/")
def read_root():
    """Endpoint raiz para verificar se o serviço está no ar."""
    return {"status": "Products Service is running!"}