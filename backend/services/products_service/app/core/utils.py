# Em core/utils.py

from typing import Optional, Tuple
from decimal import Decimal, ROUND_HALF_UP
from models.product_model import Product, CouponType
from schemas.product_schemas import ProductRead, DiscountDetails

def calculate_final_price(product: Product) -> Tuple[Decimal, Optional[DiscountDetails]]:
    if product.discount_value is None or product.discount_type is None:
        return product.price, None
    discount_details = DiscountDetails(type=product.discount_type.value, value=product.discount_value)
    if product.discount_type == CouponType.percent:
        discount_amount = (product.price * product.discount_value) / 100
        final_price = product.price - discount_amount
    elif product.discount_type == CouponType.fixed:
        final_price = product.price - product.discount_value
    else:
        return product.price, None
    final_price = max(Decimal("0.01"), final_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    return final_price, discount_details

def map_product_to_read_schema(product: Product) -> ProductRead:
    """Mapeia um objeto do modelo Product para o schema de leitura ProductRead."""
    final_price, discount_details = calculate_final_price(product)
    
    # model_dump() é a forma atualizada do .dict()
    product_data = product.model_dump() 
    
    product_data.update({
        "is_out_of_stock": product.stock == 0,
        "final_price": final_price,
        "discount": discount_details
    })
    # CORREÇÃO: Garantimos que 'deleted_at' está no dicionário antes de criar o schema
    product_data["deleted_at"] = product.deleted_at
    
    return ProductRead(**product_data)