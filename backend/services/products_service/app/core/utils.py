"""
Módulo de Funções Auxiliares (Utils)

Este arquivo centraliza lógicas reutilizáveis para manter nosso código
organizado e evitar repetição (princípio DRY - Don't Repeat Yourself).
"""
from typing import Optional, Tuple
from decimal import Decimal, ROUND_HALF_UP

from models.product_model import Product, CouponType
from schemas.product_schemas import ProductRead, DiscountDetails


def calculate_final_price(product: Product) -> Tuple[Decimal, Optional[DiscountDetails]]:
    """
    Calcula o preço final de um produto com base no desconto ativo.

    Retorna uma tupla contendo: (preço_final, detalhes_do_desconto_ou_None).
    """
    # Se não houver desconto, retorna o preço original e nenhum detalhe de desconto.
    if product.discount_value is None or product.discount_type is None:
        return product.price, None

    discount_details = DiscountDetails(type=product.discount_type.value, value=product.discount_value)
    
    # Calcula o preço com base no tipo de desconto
    if product.discount_type == CouponType.percent:
        discount_amount = (product.price * product.discount_value) / 100
        final_price = product.price - discount_amount
    elif product.discount_type == CouponType.fixed:
        final_price = product.price - product.discount_value
    else:
        # Se o tipo for inválido, retorna o preço original por segurança
        return product.price, None

    # Arredonda para 2 casas decimais e garante que o preço nunca seja menor que 0.01
    final_price_quantized = final_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    final_price = max(Decimal("0.01"), final_price_quantized)
    
    return final_price, discount_details


def map_product_to_read_schema(product: Product) -> ProductRead:
    """
    Mapeia um objeto do modelo do banco (Product) para o schema de resposta da API (ProductRead).
    
    Esta função é a "tradutora" que garante que a API sempre responda com os campos calculados,
    como 'final_price', 'is_out_of_stock' e os detalhes do desconto.
    """
    final_price, discount_details = calculate_final_price(product)
    
    # .model_dump() é a forma moderna e recomendada de converter um objeto SQLModel para dicionário
    product_data = product.model_dump() 
    
    # Adiciona os campos calculados ao dicionário
    product_data.update({
        "is_out_of_stock": product.stock == 0,
        "final_price": final_price,
        "discount": discount_details
    })
    
    # Cria e retorna uma instância do schema de resposta com todos os dados corretos
    return ProductRead(**product_data)