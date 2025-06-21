# Em api/routes/coupons.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from core.database import get_session
from models.coupon_model import Coupon
from schemas.coupon_schemas import CouponCreate, CouponRead

router = APIRouter(
    prefix="/coupons",
    tags=["Coupons"],
)

@router.post("/", response_model=CouponRead, status_code=201)
def create_coupon(*, session: Session = Depends(get_session), coupon: CouponCreate):
    """
    Cria um novo cupom de desconto.
    """
    db_coupon = Coupon.from_orm(coupon)
    
    try:
        session.add(db_coupon)
        session.commit()
        session.refresh(db_coupon)
        return db_coupon
    except IntegrityError:
        # Erro acontece se o 'code' já existir no banco (devido ao unique=True)
        session.rollback()
        raise HTTPException(
            status_code=409, # 409 Conflict
            detail=f"O cupom com o código '{coupon.code}' já existe.",
        )