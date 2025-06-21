# Em models/coupon_model.py

from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime
from decimal import Decimal

# Usaremos um Enum para garantir que o tipo do cupom seja sempre 'fixed' ou 'percent'
import enum

class CouponType(str, enum.Enum):
    fixed = "fixed"
    percent = "percent"


class Coupon(SQLModel, table=True):
    """
    Representa a tabela 'coupon' no banco de dados.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    
    code: str = Field(unique=True, index=True, max_length=20)
    
    type: CouponType
    
    # Usamos Decimal para valores monetários para evitar problemas de precisão
    value: Decimal
    
    one_shot: bool = Field(default=False)
    
    valid_from: datetime
    valid_until: datetime
    
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)