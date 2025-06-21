from fastapi import FastAPI
from sqlmodel import SQLModel

# Importações dos módulos locais
from core.database import engine
from api.routes import products

# --- IMPORTAÇÃO DOS MODELOS PARA CRIAÇÃO DAS TABELAS ---
# Ao importar os modelos aqui, garantimos que o SQLModel "saiba" da existência
# deles quando chamarmos a função 'create_all'.
from models.product_model import Product
from models.coupon_model import Coupon


def create_db_and_tables():
    """
    Cria as tabelas 'product' e 'coupon' no banco de dados se elas não existirem.
    """
    SQLModel.metadata.create_all(engine)


app = FastAPI(
    title="Products Service",
    on_startup=[create_db_and_tables], # Executa a função na inicialização
)

# Inclui as rotas do módulo de produtos
app.include_router(products.router, prefix="/api/v1")

@app.get("/")
def read_root():
    """Endpoint raiz para verificar se o serviço está no ar."""
    return {"status": "Products Service is running!"}