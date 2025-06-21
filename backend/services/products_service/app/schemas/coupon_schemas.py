# Em schemas/coupon_schemas.py

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional
import re

from pydantic import validator
from sqlmodel import SQLModel

from models.coupon_model import CouponType

class CouponBase(SQLModel):
    """Schema base para cupons, com validações."""
    code: str
    type: CouponType
    value: Decimal
    one_shot: bool = False
    valid_from: datetime
    valid_until: datetime

    # Validador para o código do cupom
    @validator("code")
    def validate_and_normalize_code(cls, v):
        if not (4 <= len(v) <= 20):
            raise ValueError("O código deve ter entre 4 e 20 caracteres.")
        if not re.match("^[a-zA-Z0-9]+$", v):
            raise ValueError("O código deve conter apenas caracteres alfanuméricos.")
        
        # Normalização: remove espaços e converte para minúsculas
        normalized_code = v.strip().lower()
        
        # Validação de palavras reservadas
        reserved_words = ["admin", "auth", "null", "undefined"]
        if normalized_code in reserved_words:
            raise ValueError(f"O código '{normalized_code}' é uma palavra reservada.")
            
        return normalized_code

    # Validador para o valor do cupom, dependendo do tipo
    @validator("value")
    def validate_value_based_on_type(cls, v, values):
        if 'type' in values:
            coupon_type = values['type']
            if coupon_type == CouponType.percent and not (1 <= v <= 80):
                raise ValueError("Desconto percentual deve estar entre 1 e 80.")
            if coupon_type == CouponType.fixed and v <= 0:
                raise ValueError("Desconto fixo deve ser um valor positivo.")
        return v

    # Validador para as datas de validade
    @validator("valid_until")
    def validate_dates(cls, v, values):
        if 'valid_from' in values and v <= values['valid_from']:
            raise ValueError("A data de expiração deve ser posterior à data de início.")
        
        five_years_from_start = values['valid_from'] + timedelta(days=365*5)
        if v > five_years_from_start:
            raise ValueError("A validade do cupom não pode exceder 5 anos.")
            
        return v


class CouponCreate(CouponBase):
    """Schema para criar um cupom. Herda as validações do base."""
    pass

class CouponRead(CouponBase):
    """Schema para ler/retornar os dados de um cupom."""
    id: int
    created_at: datetime
    deleted_at: Optional[datetime] = None