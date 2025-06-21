# Em schemas/product_schemas.py

from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel

# Novo schema para detalhar o desconto que será exibido na API
class DiscountDetails(SQLModel):
    type: str
    value: Decimal

# Schema de criação/atualização usa Decimal para o preço
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

# Schema de leitura é o mais modificado, para mostrar os novos campos calculados
class ProductRead(SQLModel):
    id: int
    name: str
    description: Optional[str] = None
    price: Decimal          # Preço original
    stock: int
    created_at: datetime
    is_out_of_stock: bool
    final_price: Decimal    # Preço com desconto, que será calculado
    discount: Optional[DiscountDetails] = None # Detalhes do desconto, se houver

# Schemas de paginação
class PaginatedMetadata(SQLModel):
    page: int
    limit: int
    totalItems: int
    totalPages: int

class ProductPage(SQLModel):
    data: List[ProductRead]
    meta: PaginatedMetadata