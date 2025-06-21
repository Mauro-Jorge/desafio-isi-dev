# Em tests/test_products.py

from fastapi.testclient import TestClient
from decimal import Decimal

# O 'client' aqui é injetado automaticamente pela fixture que criamos no conftest.py
def test_product_lifecycle(client: TestClient):
    # 1. Criar um produto
    response = client.post(
        "/api/v1/products/",
        json={"name": "Produto de Teste", "description": "Desc", "price": 10.50, "stock": 100},
    )
    assert response.status_code == 201
    data = response.json()
    product_id = data["id"]
    assert data["name"] == "Produto de Teste"
    assert data["final_price"] == "10.50" # Preços vêm como string em JSON

    # 2. Buscar o produto criado
    response = client.get(f"/api/v1/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["id"] == product_id

    # 3. Atualizar o produto
    response = client.patch(
        f"/api/v1/products/{product_id}",
        json={"price": "12.00"}, # Enviamos como string, assim como receberíamos de um frontend
    )
    assert response.status_code == 200
    assert response.json()["price"] == "12.00"

    # 4. Deletar (soft delete) o produto
    response = client.delete(f"/api/v1/products/{product_id}")
    assert response.status_code == 204

    # 5. Verificar se não é mais encontrado
    response = client.get(f"/api/v1/products/{product_id}")
    assert response.status_code == 404

    # 6. Restaurar o produto
    response = client.post(f"/api/v1/products/{product_id}/restore")
    assert response.status_code == 200
    assert response.json()["deleted_at"] is None

    # 7. Verificar se está ativo novamente
    response = client.get(f"/api/v1/products/{product_id}")
    assert response.status_code == 200