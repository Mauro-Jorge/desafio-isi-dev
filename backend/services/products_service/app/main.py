from fastapi import FastAPI
from sqlmodel import SQLModel

# Importações dos módulos locais
from core.database import engine
# ALTERAÇÃO 1: Importa o novo roteador de cupons junto com o de produtos
from api.routes import products, coupons

# --- IMPORTAÇÃO DOS MODELOS PARA CRIAÇÃO DAS TABELAS ---
from models.product_model import Product
from models.coupon_model import Coupon


def create_db_and_tables():
    """
    Cria as tabelas no banco de dados se elas não existirem.
    """
    SQLModel.metadata.create_all(engine)


app = FastAPI(
    title="Products Service",
    on_startup=[create_db_and_tables],
)

# Registra os roteadores na aplicação principal
app.include_router(products.router, prefix="/api/v1")
# ALTERAÇÃO 2: Registra o novo roteador de cupons
app.include_router(coupons.router, prefix="/api/v1")

@app.get("/")
def read_root():
    """Endpoint raiz para verificar se o serviço está no ar."""
    return {"status": "Products Service is running!"}