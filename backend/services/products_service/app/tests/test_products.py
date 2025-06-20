from fastapi.testclient import TestClient
from app.main import app # Importa a instância da sua aplicação

# Cria um cliente de teste que pode fazer requisições à sua app
client = TestClient(app)

def test_read_root():
    """
    Testa se o endpoint raiz ("/") está funcionando e retorna o status esperado.
    """
    response = client.get("/")
    # Verifica se o status code da resposta é 200 (OK)
    assert response.status_code == 200
    # Verifica se o corpo da resposta é o JSON esperado
    assert response.json() == {"message": "Products Service is running"}