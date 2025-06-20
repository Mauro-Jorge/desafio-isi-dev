from typing import List, Optional
from datetime import datetime
from sqlmodel import SQLModel

# --- Schemas para um único produto ---

class ProductCreate(SQLModel):
    """Schema para criar um novo produto."""
    name: str
    description: str | None = None
    price: float
    stock: int

class ProductRead(SQLModel):
    """Schema para ler/retornar os dados de um produto."""
    id: int
    name: str
    description: str | None = None
    price: float
    stock: int
    created_at: datetime

class ProductUpdate(SQLModel):
    """Schema para atualizar um produto, com todos os campos opcionais."""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None

# --- Schemas para a resposta paginada ---

class PaginatedMetadata(SQLModel):
    """Schema para os metadados de paginação."""
    page: int
    limit: int
    totalItems: int
    totalPages: int

class ProductPage(SQLModel):
    """Schema para a resposta da página de produtos, contendo os dados e os metadados."""
    data: List[ProductRead]
    meta: PaginatedMetadata