"""Pruebas de que los endpoints básicos de la API responden correctamente.

Usa TestClient (in-process) para no depender de un servidor en localhost:8000.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    """Probar el endpoint de health check."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint():
    """Probar el endpoint raíz."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data.get("docs") == "/docs"


def test_docs():
    """Probar que la documentación Swagger está disponible."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_schema():
    """Probar que el schema OpenAPI está disponible."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "info" in schema
    assert "paths" in schema
    assert "title" in schema["info"]
    assert "version" in schema["info"]


def main():
    """Ejecutar las pruebas (para uso como script: python -m tests.integration.test_api)."""
    import sys

    # Reutilizar pytest desde aquí no es habitual; se puede ejecutar con:
    # pytest tests/integration/test_api.py -v
    print("Ejecuta: pytest tests/integration/test_api.py -v")
    sys.exit(0)


if __name__ == "__main__":
    main()
