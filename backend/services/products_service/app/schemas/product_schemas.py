# Em schemas/product_schemas.py

from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel

class DiscountDetails(SQLModel):
    type: str
    value: Decimal

class ProductCreate(SQLModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    stock: int

class ProductUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None

class ProductRead(SQLModel):
    id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    stock: int
    created_at: datetime
    is_out_of_stock: bool
    final_price: Decimal
    discount: Optional[DiscountDetails] = None
    # CORREÇÃO: Adicionamos o campo que faltava
    deleted_at: Optional[datetime] = None

# ... (O resto do arquivo - PaginatedMetadata e ProductPage - continua igual)
class PaginatedMetadata(SQLModel):
    page: int
    limit: int
    totalItems: int
    totalPages: int

class ProductPage(SQLModel):
    data: List[ProductRead]
    meta: PaginatedMetadata