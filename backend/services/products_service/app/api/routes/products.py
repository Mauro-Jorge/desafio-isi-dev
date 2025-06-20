from fastapi import APIRouter, Depends
from sqlmodel import Session

# ANTES: from app.core.database import get_session | from app.models...
# DEPOIS (CORRETO):
from core.database import get_session
from models.product_model import Product
from schemas.product_schemas import ProductCreate, ProductRead

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)

@router.post("/", response_model=ProductRead, status_code=201)
def create_product(*, session: Session = Depends(get_session), product: ProductCreate):
    """
    Cria um novo produto no banco de dados.
    """
    db_product = Product.from_orm(product)
    
    session.add(db_product)
    
    session.commit()
    
    session.refresh(db_product)
    
    return db_product