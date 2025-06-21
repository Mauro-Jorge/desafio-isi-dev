from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Importa o middleware de CORS
from sqlmodel import SQLModel

from core.database import engine
from api.routes import products, coupons
from models.product_model import Product
from models.coupon_model import Coupon

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

app = FastAPI(
    title="Products Service",
    on_startup=[create_db_and_tables],
)

# --- INÍCIO DA CONFIGURAÇÃO DO CORS ---

# Lista de origens que têm permissão para fazer requisições à nossa API
origins = [
    "http://localhost:5173", # Endereço do nosso frontend em desenvolvimento
    # Você poderia adicionar outros endereços aqui, como o da aplicação em produção
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # Permite as origens listadas
    allow_credentials=True,       # Permite cookies (se usarmos no futuro)
    allow_methods=["*"],          # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],          # Permite todos os cabeçalhos
)
# --- FIM DA CONFIGURAÇÃO DO CORS ---


# O resto da aplicação continua como estava
app.include_router(products.router, prefix="/api/v1")
app.include_router(coupons.router, prefix="/api/v1")

@app.get("/")
def read_root():
    """Endpoint raiz para verificar se o serviço está no ar."""
    return {"status": "Products Service is running!"}