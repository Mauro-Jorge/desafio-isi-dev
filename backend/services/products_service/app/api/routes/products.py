# Em api/routes/products.py (Versão Corrigida e Reorganizada)

import math
from typing import List
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, Query, HTTPException, Response, status
from pydantic import BaseModel, Field as PydanticField
from sqlmodel import Session, select, func

from core.database import get_session
from core.utils import map_product_to_read_schema
from models.product_model import Product, CouponType
from models.coupon_model import Coupon
from schemas.product_schemas import (
    ProductCreate, ProductRead, ProductUpdate, ProductPage, PaginatedMetadata
)

class PercentDiscountApply(BaseModel):
    value: Decimal = PydanticField(..., gt=0, le=80)

class CouponDiscountApply(BaseModel):
    code: str = PydanticField(..., min_length=4, max_length=20)

router = APIRouter(prefix="/products", tags=["Products"])

# --- ORDEM DE ROTAS CORRIGIDA ---

# 1. Rota de Listagem GET /
@router.get("/", response_model=ProductPage)
def read_products(
    *, session: Session = Depends(get_session), page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50), search: str = Query(None),
    minPrice: float = Query(None, ge=0), maxPrice: float = Query(None, ge=0),
    sortBy: str = Query("created_at"), sortOrder: str = Query("desc"),
    includeDeleted: bool = Query(False)
):
    query = select(Product)
    if search:
        query = query.where(Product.name.contains(search) | Product.description.contains(search))
    if minPrice is not None:
        query = query.where(Product.price >= minPrice)
    if maxPrice is not None:
        query = query.where(Product.price <= maxPrice)
    if not includeDeleted:
        query = query.where(Product.deleted_at == None)

    count_query = select(func.count()).select_from(query.subquery())
    # CORREÇÃO FINAL: O método correto é .one() ou .scalar(), não .scalar_one()
    total_items = session.exec(count_query).one()

    sort_column = getattr(Product, sortBy, Product.created_at)
    if sortOrder.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    offset = (page - 1) * limit
    paginated_query = query.offset(offset).limit(limit)
    products = session.exec(paginated_query).all()

    product_reads = [map_product_to_read_schema(p) for p in products]
    
    total_pages = math.ceil(total_items / limit) if total_items > 0 else 0
    return ProductPage(
        data=product_reads,
        meta=PaginatedMetadata(page=page, limit=limit, totalItems=total_items, totalPages=total_pages)
    )

# 2. Rota de Criação POST /
@router.post("/", response_model=ProductRead, status_code=201)
def create_product(*, session: Session = Depends(get_session), product: ProductCreate):
    db_product = Product.from_orm(product)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return map_product_to_read_schema(db_product)

# 3. Rotas específicas que vêm antes da rota genérica com {id}
# ... (aqui entrariam as rotas de restore, discount, etc.)
# ... vou omitir para manter o foco na correção, mas elas devem estar aqui

# 4. Rota genérica GET /{id} por último
@router.get("/{product_id}", response_model=ProductRead)
def read_product(*, session: Session = Depends(get_session), product_id: int):
    product = session.get(Product, product_id)
    if not product or product.deleted_at:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return map_product_to_read_schema(product)

# ... (aqui entrariam as outras rotas PATCH, DELETE, etc.)