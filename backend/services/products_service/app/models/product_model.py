from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime

class Product(SQLModel, table=True):
    """
    Representa a tabela 'product' no banco de dados.
    Cada atributo da classe é uma coluna na tabela.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: Optional[str] = Field(default=None)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    
    # CAMPO ADICIONADO PARA O SOFT DELETE
    # Por padrão, é nulo. Quando um produto for "deletado",
    # este campo receberá a data e hora da exclusão.
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)