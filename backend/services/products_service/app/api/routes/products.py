# Em api/routes/products.py (Versão com Aplicação de Cupom)

import math
from typing import List
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, Query, HTTPException, Response, status
from pydantic import BaseModel, Field as PydanticField
from sqlmodel import Session, select, func

from core.database import get_session
from core.utils import map_product_to_read_schema
# Precisamos dos modelos de Produto e Cupom neste arquivo
from models.product_model import Product, CouponType
from models.coupon_model import Coupon
from schemas.product_schemas import (
    ProductCreate, ProductRead, ProductUpdate, ProductPage, PaginatedMetadata
)

# --- Schemas para os corpos das requisições de desconto ---

class PercentDiscountApply(BaseModel):
    value: Decimal = PydanticField(..., gt=0, le=80, description="Percentual de desconto (1-80)")

class CouponDiscountApply(BaseModel):
    code: str = PydanticField(..., min_length=4, max_length=20, description="Código do cupom promocional")


router = APIRouter(prefix="/products", tags=["Products"])

# --- Endpoints de CRUD e Restore (sem alterações) ---
@router.post("/", response_model=ProductRead, status_code=201)
def create_product(*, session: Session = Depends(get_session), product: ProductCreate):
    db_product = Product.from_orm(product)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return map_product_to_read_schema(db_product)

# ... (as rotas GET, PATCH, DELETE, RESTORE continuam aqui exatamente como antes)
@router.get("/{product_id}", response_model=ProductRead)
def read_product(*, session: Session = Depends(get_session), product_id: int):
    product = session.get(Product, product_id)
    if not product or product.deleted_at:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return map_product_to_read_schema(product)

@router.patch("/{product_id}", response_model=ProductRead)
def update_product(*, session: Session = Depends(get_session), product_id: int, product_update: ProductUpdate):
    db_product = session.get(Product, product_id)
    if not db_product or db_product.deleted_at:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    update_data = product_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return map_product_to_read_schema(db_product)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(*, session: Session = Depends(get_session), product_id: int):
    product = session.get(Product, product_id)
    if not product or product.deleted_at:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    product.deleted_at = datetime.utcnow()
    session.add(product)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/{product_id}/restore", response_model=ProductRead)
def restore_product(*, session: Session = Depends(get_session), product_id: int):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    if not product.deleted_at:
        raise HTTPException(status_code=409, detail="O produto já está ativo")
    product.deleted_at = None
    session.add(product)
    session.commit()
    session.refresh(product)
    return map_product_to_read_schema(product)


# --- Endpoints de Desconto ---

@router.post("/{product_id}/discount/percent", response_model=ProductRead)
def apply_percent_discount(*, session: Session = Depends(get_session), product_id: int, discount_payload: PercentDiscountApply):
    """Aplica um desconto percentual direto a um produto."""
    db_product = session.get(Product, product_id)
    if not db_product or db_product.deleted_at:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    if db_product.discount_value is not None:
        raise HTTPException(status_code=409, detail="Um desconto já está ativo neste produto.")
    
    discount_amount = (db_product.price * discount_payload.value) / 100
    final_price = db_product.price - discount_amount
    if final_price < Decimal("0.01"):
        raise HTTPException(status_code=422, detail="O desconto resulta em um preço final menor que R$ 0,01.")

    db_product.discount_type = CouponType.percent
    db_product.discount_value = discount_payload.value
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return map_product_to_read_schema(db_product)

# NOVO ENDPOINT PARA APLICAR DESCONTO VIA CUPOM
@router.post("/{product_id}/discount/coupon", response_model=ProductRead)
def apply_coupon_discount(
    *,
    session: Session = Depends(get_session),
    product_id: int,
    discount_payload: CouponDiscountApply
):
    """Aplica um cupom de desconto a um produto."""
    # 1. Validações iniciais
    db_product = session.get(Product, product_id)
    if not db_product or db_product.deleted_at:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    if db_product.discount_value is not None:
        raise HTTPException(status_code=409, detail="Um desconto já está ativo neste produto.")
    
    # 2. Busca e valida o cupom
    normalized_code = discount_payload.code.lower()
    coupon_query = select(Coupon).where(Coupon.code == normalized_code, Coupon.deleted_at == None)
    db_coupon = session.exec(coupon_query).first()
    if not db_coupon:
        raise HTTPException(status_code=404, detail="Cupom inválido.")
    
    now = datetime.utcnow()
    if not (db_coupon.valid_from <= now <= db_coupon.valid_until):
        raise HTTPException(status_code=400, detail="Cupom expirado ou ainda não válido.")
        
    # 3. Calcula o preço final e valida
    if db_coupon.type == CouponType.percent:
        discount_amount = (db_product.price * db_coupon.value) / 100
        final_price = db_product.price - discount_amount
    else: # tipo 'fixed'
        final_price = db_product.price - db_coupon.value
        
    if final_price < Decimal("0.01"):
        raise HTTPException(status_code=422, detail="O cupom resulta em um preço final menor que R$ 0,01.")
        
    # 4. Aplica o desconto ao produto
    db_product.discount_type = db_coupon.type
    db_product.discount_value = db_coupon.value
    db_product.coupon_id = db_coupon.id # Vincula o ID do cupom ao produto
    
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    
    return map_product_to_read_schema(db_product)


# GET / (Listagem) - Precisa ser o último para não conflitar com rotas mais específicas
@router.get("/", response_model=ProductPage)
def read_products(*, session: Session = Depends(get_session), page: int = Query(1, ge=1),
    # ... (restante dos parâmetros da função)
):
    # (A lógica interna desta função continua a mesma)
    # ...
    pass # Apenas para encurtar o exemplo, a lógica completa já está no seu arquivo