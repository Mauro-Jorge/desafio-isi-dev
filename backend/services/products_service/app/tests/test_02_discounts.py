# Em: tests/test_02_discounts.py

from fastapi.testclient import TestClient
from decimal import Decimal
from datetime import datetime, timedelta

# As fixtures 'client' e 'session' são injetadas automaticamente pelo conftest.py
def test_discount_application_flow(client: TestClient):
    """
    Testa o fluxo completo: 
    1. Cria um cupom e um produto.
    2. Aplica o cupom ao produto.
    3. Verifica se o desconto e o preço final estão corretos.
    4. Tenta aplicar um segundo desconto e espera um erro.
    5. Remove o desconto.
    6. Verifica se o produto voltou ao estado original.
    """
    # ETAPA 1: Criar um cupom válido para o teste
    coupon_code = "desconto25"
    valid_from = datetime.utcnow() - timedelta(days=1)
    valid_until = datetime.utcnow() + timedelta(days=1)
    
    response_coupon = client.post(
        "/api/v1/coupons/",
        json={
            "code": coupon_code,
            "type": "percent",
            "value": 25, # 25% de desconto
            "one_shot": False,
            "valid_from": valid_from.isoformat(),
            "valid_until": valid_until.isoformat(),
        },
    )
    assert response_coupon.status_code == 201

    # ETAPA 2: Crie um produto para aplicar o desconto
    response_product = client.post(
        "/api/v1/products/",
        json={"name": "Produto para Desconto", "description": "Teste de desconto", "price": "200.00", "stock": 50},
    )
    assert response_product.status_code == 201
    product_id = response_product.json()["id"]

    # ETAPA 3: Aplique o cupom ao produto
    response_apply = client.post(
        f"/api/v1/products/{product_id}/discount/coupon",
        json={"code": coupon_code}
    )
    assert response_apply.status_code == 200
    
    # ETAPA 4: Verifique se o desconto foi aplicado corretamente
    data = response_apply.json()
    assert Decimal(data["price"]) == Decimal("200.00")
    # Preço final esperado: 200 - 25% = 150
    assert Decimal(data["final_price"]) == Decimal("150.00")
    assert data["discount"]["type"] == "percent"
    assert Decimal(data["discount"]["value"]) == Decimal("25")

    # ETAPA 5: Tente aplicar um segundo desconto e espere um erro 409 (Conflito)
    response_conflict = client.post(
        f"/api/v1/products/{product_id}/discount/percent",
        json={"value": 10}
    )
    assert response_conflict.status_code == 409

    # ETAPA 6: Remova o desconto
    response_remove = client.delete(f"/api/v1/products/{product_id}/discount")
    assert response_remove.status_code == 204

    # ETAPA 7: Verifique se o produto voltou ao normal
    response_final = client.get(f"/api/v1/products/{product_id}")
    assert response_final.status_code == 200
    data_final = response_final.json()
    assert Decimal(data_final["price"]) == Decimal("200.00")
    assert Decimal(data_final["final_price"]) == Decimal("200.00")
    assert data_final["discount"] is None