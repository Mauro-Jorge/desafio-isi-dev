# Em api/routes/coupons.py

import math
from typing import List
from datetime import datetime # Importação necessária para o soft delete

# Adicionamos Response e status para o retorno 204
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select, func

from core.database import get_session
from models.coupon_model import Coupon
from schemas.coupon_schemas import (
    CouponCreate, 
    CouponRead, 
    CouponUpdate,
    CouponPage, 
    PaginatedMetadata
)

router = APIRouter(
    prefix="/coupons",
    tags=["Coupons"],
)

# ... (as rotas POST, GET/{code}, PATCH/{code} continuam aqui, sem alterações)
@router.post("/", response_model=CouponRead, status_code=201)
def create_coupon(*, session: Session = Depends(get_session), coupon: CouponCreate):
    """Cria um novo cupom de desconto."""
    db_coupon = Coupon.from_orm(coupon)
    try:
        session.add(db_coupon)
        session.commit()
        session.refresh(db_coupon)
        return db_coupon
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail=f"O cupom com o código '{coupon.code}' já existe.")

@router.get("/{code}", response_model=CouponRead)
def read_coupon(*, session: Session = Depends(get_session), code: str):
    """Retorna os detalhes de um cupom específico pelo seu código."""
    normalized_code = code.lower()
    query = select(Coupon).where(Coupon.code == normalized_code, Coupon.deleted_at == None)
    coupon = session.exec(query).first()
    if not coupon:
        raise HTTPException(status_code=404, detail="Cupom não encontrado")
    return coupon

@router.patch("/{code}", response_model=CouponRead)
def update_coupon(*, session: Session = Depends(get_session), code: str, coupon_update: CouponUpdate):
    """Atualiza parcialmente um cupom existente."""
    normalized_code = code.lower()
    query = select(Coupon).where(Coupon.code == normalized_code, Coupon.deleted_at == None)
    db_coupon = session.exec(query).first()
    if not db_coupon:
        raise HTTPException(status_code=404, detail="Cupom não encontrado")
    update_data = coupon_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_coupon, key, value)
    session.add(db_coupon)
    session.commit()
    session.refresh(db_coupon)
    return db_coupon

# --- NOVA ROTA PARA FAZER O SOFT DELETE DE UM CUPOM ---
@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_coupon(*, session: Session = Depends(get_session), code: str):
    """Marca um cupom como deletado (soft delete)."""
    normalized_code = code.lower()
    query = select(Coupon).where(Coupon.code == normalized_code, Coupon.deleted_at == None)
    coupon = session.exec(query).first()

    if not coupon:
        raise HTTPException(status_code=404, detail="Cupom não encontrado ou já deletado")

    coupon.deleted_at = datetime.utcnow()
    session.add(coupon)
    session.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/", response_model=CouponPage)
def read_coupons(
    *,
    session: Session = Depends(get_session),
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(10, ge=1, le=50, description="Itens por página"),
    search: str = Query(None, description="Busca textual no código do cupom")
):
    """Retorna uma lista paginada e filtrada de cupons ativos."""
    query = select(Coupon).where(Coupon.deleted_at == None)
    if search:
        query = query.where(Coupon.code.contains(search.lower()))
    
    count_query = select(func.count()).select_from(query.subquery())
    total_items = session.exec(count_query).scalar_one()

    offset = (page - 1) * limit
    paginated_query = query.order_by(Coupon.created_at.desc()).offset(offset).limit(limit)
    
    coupons = session.exec(paginated_query).all()
    
    total_pages = math.ceil(total_items / limit) if total_items > 0 else 0
    return CouponPage(
        data=coupons,
        meta=PaginatedMetadata(
            page=page,
            limit=limit,
            totalItems=total_items,
            totalPages=total_pages
        )
    )