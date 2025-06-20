from sqlmodel import SQLModel
from datetime import datetime

class ProductCreate(SQLModel):
    name: str
    description: str | None = None
    price: float
    stock: int

class ProductRead(SQLModel):
    id: int
    name: str
    description: str | None = None
    price: float
    stock: int
    created_at: datetime