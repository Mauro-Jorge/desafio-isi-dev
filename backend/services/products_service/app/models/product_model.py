from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: Optional[str] = Field(default=None)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)