import pytest
from flask import json
from app import create_app 
from app.services import CommerceService
from unittest.mock import patch

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@patch.object(CommerceService, 'comprar')
def test_comprar(mock_comprar, client):
    mock_comprar.return_value = None  # No importa el retorno en este caso
    carrito_data = {"producto": 1, "direccion_envio": "Calle 123"}
    response = client.post("/commerce/comprar", data=json.dumps(carrito_data), content_type='application/json')
    
    assert response.status_code == 200
    assert response.json == {"microservicio": "Orquestador", "status": "ok"}
    mock_comprar.assert_called_once()

@patch.object(CommerceService, 'consultar_catalogo')
def test_consultar_catalogo_existente(mock_consultar, client):
    mock_consultar.return_value = {"id": 1, "nombre": "Producto de prueba"}
    response = client.get("/commerce/consultar/catalogo/1")
    
    assert response.status_code == 200
    assert response.json == {"id": 1, "nombre": "Producto de prueba"}
    mock_consultar.assert_called_once_with(1)

@patch.object(CommerceService, 'consultar_catalogo')
def test_consultar_catalogo_no_existente(mock_consultar, client):
    mock_consultar.return_value = None
    response = client.get("/commerce/consultar/catalogo/999")
    
    assert response.status_code == 404
    assert response.json == {"message": "No se encontró el producto"}
    mock_consultar.assert_called_once_with(999)

def test_consultar_catalogo_error(client):
    response = client.get("/commerce/consultar/catalogo/abc")  # ID inválido
    assert response.status_code == 404
