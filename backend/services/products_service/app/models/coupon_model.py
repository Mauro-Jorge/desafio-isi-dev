# Em models/coupon_model.py

from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime
from decimal import Decimal
import enum

from sqlalchemy import Column
from sqlalchemy.types import DECIMAL

class CouponType(str, enum.Enum):
    fixed = "fixed"
    percent = "percent"

class Coupon(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(unique=True, index=True, max_length=20)
    type: CouponType
    
    # FORMA CORRETA de definir um campo Decimal com precisão
    value: Decimal = Field(
        sa_column=Column(DECIMAL(10, 2), nullable=False)
    )
    
    one_shot: bool = Field(default=False)
    valid_from: datetime
    valid_until: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)