from typing import List
import math
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session, select, func

# Importações diretas dos nossos módulos
from core.database import get_session
from models.product_model import Product
from schemas.product_schemas import (
    ProductCreate, 
    ProductRead, 
    ProductUpdate,
    ProductPage, 
    PaginatedMetadata
)

# Cria um roteador específico para os endpoints de produtos
router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.post("/", response_model=ProductRead, status_code=201)
def create_product(*, session: Session = Depends(get_session), product: ProductCreate):
    """Cria um novo produto."""
    db_product = Product.from_orm(product)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


@router.get("/{product_id}", response_model=ProductRead)
def read_product(*, session: Session = Depends(get_session), product_id: int):
    """Retorna os detalhes de um produto específico pelo seu ID."""
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return product


@router.patch("/{product_id}", response_model=ProductRead)
def update_product(
    *, 
    session: Session = Depends(get_session), 
    product_id: int, 
    product_update: ProductUpdate
):
    """Atualiza parcialmente um produto existente."""
    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    update_data = product_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)

    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


@router.get("/", response_model=ProductPage)
def read_products(
    *,
    session: Session = Depends(get_session),
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(10, ge=1, le=50, description="Itens por página"),
    search: str = Query(None, description="Busca textual no nome ou descrição"),
    minPrice: float = Query(None, ge=0, description="Preço mínimo"),
    maxPrice: float = Query(None, ge=0, description="Preço máximo"),
    sortBy: str = Query("created_at", description="Campo para ordenação: name, price, stock, created_at"),
    sortOrder: str = Query("desc", description="Ordem: asc ou desc")
):
    """Retorna uma lista paginada e filtrada de produtos."""
    # Monta a query de filtros
    query = select(Product)
    if search:
        query = query.where(Product.name.contains(search) | Product.description.contains(search))
    if minPrice is not None:
        query = query.where(Product.price >= minPrice)
    if maxPrice is not None:
        query = query.where(Product.price <= maxPrice)

    # Executa uma query de contagem otimizada
    count_query = select(func.count()).select_from(query.subquery())
    total_items = session.exec(count_query).scalar_one()

    # Adiciona ordenação e paginação
    sort_column = getattr(Product, sortBy, Product.created_at)
    if sortOrder.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    offset = (page - 1) * limit
    paginated_query = query.offset(offset).limit(limit)

    # Executa a query final
    products = session.exec(paginated_query).all()
    
    # Calcula e monta a resposta
    total_pages = math.ceil(total_items / limit) if total_items > 0 else 0
    return ProductPage(
        data=products,
        meta=PaginatedMetadata(
            page=page,
            limit=limit,
            totalItems=total_items,
            totalPages=total_pages
        )
    )