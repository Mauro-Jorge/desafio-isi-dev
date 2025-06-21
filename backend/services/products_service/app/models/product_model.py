# Em models/product_model.py

from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime
from decimal import Decimal
import enum

# Importações necessárias do SQLAlchemy para definir o tipo de coluna
from sqlalchemy import Column
from sqlalchemy.types import DECIMAL

class CouponType(str, enum.Enum):
    fixed = "fixed"
    percent = "percent"

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: Optional[str] = Field(default=None)
    
    # FORMA CORRETA de definir um campo Decimal com precisão para o banco de dados
    price: Decimal = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=False),
        gt=0
    )
    
    stock: int = Field(ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)

    discount_type: Optional[CouponType] = Field(default=None, nullable=True)
    
    discount_value: Optional[Decimal] = Field(
        default=None,
        sa_column=Column(DECIMAL(10, 2), nullable=True)
    )
    
    coupon_id: Optional[int] = Field(default=None, foreign_key="coupon.id", nullable=True)