"""Tests para los endpoints de ventas."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.data_store import data_store
import pandas as pd


# Crear un TestClient
client = TestClient(app)

# Sobrescribir el data_store con datos de prueba
df_test = pd.DataFrame({
    "FECHA": pd.to_datetime(["2024-01-01", "2024-02-01", "2024-03-01"]),
    "CANAL": ["POS", "WEB", "POS"],
    "CODIGO_PRODUCTO": [101, 102, 101],
    "UNIDADES": [1, 2, 1],
    "MONTO_APLICADO": [1000, 2000, 3000],
    "LOCAL": [1, 2, 1],
    "ID_PERSONA": ["uuid1", "uuid2", "uuid3"],
    "GENERO": ["Masculino", "Femenino", "Masculino"],
    "EDAD": [30, 40, 50],
})

# Inyectar datos en el singleton
data_store.set_dataframe(df_test)


class TestEndpoints:
    """Tests para los endpoints GET y POST de /v1/estadisticas/ventas."""

    def test_health_check(self):
        """Verifica que el endpoint de health funciona correctamente."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["datos_cargados"] is True
        assert response.json()["total_filas"] == 3

    def test_get_estadisticas_sin_filtros(self):
        """Verifica GET sin filtros (estadísticas de todo el dataset)."""
        response = client.get("/v1/estadisticas/ventas")
        assert response.status_code == 200
        data = response.json()
        assert data["suma"] == 6000.0
        assert data["conteo"] == 3
        assert data["promedio"] == 2000.0

    def test_get_estadisticas_con_filtros(self):
        """Verifica GET con query params."""
        response = client.get("/v1/estadisticas/ventas", params={"GENERO": "Masculino"})
        assert response.status_code == 200
        data = response.json()
        assert data["suma"] == 4000.0
        assert data["conteo"] == 2
        assert data["promedio"] == 2000.0

    def test_post_estadisticas_con_filtros(self):
        """Verifica POST con filtros en el body."""
        payload = {
            "consultas": [
                {"consulta": "CANAL", "valor": "POS"},
                {"consulta": "LOCAL", "valor": "1"}
            ]
        }
        response = client.post("/v1/estadisticas/ventas", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["conteo"] == 2
        assert data["suma"] == 4000.0

    def test_post_estadisticas_sin_resultados(self):
        """Verifica que si no hay resultados se retorna 200 OK con conteo 0."""
        payload = {
            "consultas": [
                {"consulta": "CANAL", "valor": "APP"}  # No existe en df_test
            ]
        }
        response = client.post("/v1/estadisticas/ventas", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["conteo"] == 0
        assert data["suma"] == 0.0
        assert data["promedio"] == 0.0

    def test_404_not_found_format(self):
        """Verifica que el error 404 siga el formato estricto RFC 7807."""
        response = client.get("/v1/estadisticas/endpoint_invalido")
        assert response.status_code == 404
        data = response.json()
        assert data["errorCode"] == "HTTP"
        assert data["errorLabel"] == "Not Found"
        assert "instance" in data
        assert "timestamp" in data
        assert "Not Found" in data["detail"]

    def test_post_estadisticas_filtro_invalido(self):
        """Verifica el error de validación 400 con un filtro inválido."""
        payload = {
            "consultas": [
                {"consulta": "GENERO", "valor": "Extraterrestre"}
            ]
        }
        response = client.post("/v1/estadisticas/ventas", json=payload)
        assert response.status_code == 400
        assert response.json()["errorCode"] == "VF"
        assert "no es válido para GENERO" in response.json()["detail"]
        assert response.json()["method"] == "POST"

    def test_get_estadisticas_filtro_invalido(self):
        """Verifica el error de validación 400 en GET con query param inválido."""
        response = client.get("/v1/estadisticas/ventas", params={"EDAD": "joven"})
        assert response.status_code == 400
        assert response.json()["errorCode"] == "VF"
        assert "EDAD" in response.json()["detail"]
        assert response.json()["method"] == "GET"
