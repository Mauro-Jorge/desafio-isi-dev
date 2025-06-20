# Arquivo: backend/services/products_service/app/api/routes/products.py (Completo com Soft Delete)

from typing import List
import math
from datetime import datetime

# Adicionado 'Response' e 'status' para o endpoint DELETE
from fastapi import APIRouter, Depends, Query, HTTPException, Response, status
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
    """Retorna os detalhes de um produto específico (e ativo) pelo seu ID."""
    product = session.get(Product, product_id)
    # MODIFICAÇÃO: Retorna 404 se o produto não existir OU se estiver deletado
    if not product or product.deleted_at:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return product


@router.patch("/{product_id}", response_model=ProductRead)
def update_product(*, session: Session = Depends(get_session), product_id: int, product_update: ProductUpdate):
    """Atualiza parcialmente um produto existente."""
    db_product = session.get(Product, product_id)
    # MODIFICAÇÃO: Garante que não se pode atualizar um produto deletado
    if not db_product or db_product.deleted_at:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    update_data = product_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)

    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product

# NOVO ENDPOINT: Rota para fazer o Soft Delete
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(*, session: Session = Depends(get_session), product_id: int):
    """Marca um produto como deletado (soft delete)."""
    product = session.get(Product, product_id)
    # Retorna 404 se o produto não existir ou se já estiver deletado
    if not product or product.deleted_at:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    # Define a data de exclusão e salva
    product.deleted_at = datetime.utcnow()
    session.add(product)
    session.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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
    sortOrder: str = Query("desc", description="Ordem: asc ou desc"),
    # NOVO PARÂMETRO: para incluir produtos deletados na busca
    includeDeleted: bool = Query(False, description="Incluir produtos inativos na busca")
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
    
    # MODIFICAÇÃO: Por padrão, busca apenas produtos ativos
    if not includeDeleted:
        query = query.where(Product.deleted_at == None)

    # Executa a query de contagem otimizada
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

    products = session.exec(paginated_query).all()
    
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