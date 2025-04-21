from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

# Client de test pour les appels API
client = TestClient(app)

# Headers avec une clé API valide pour les tests
API_HEADERS = {"X-API-Key": settings.API_KEY}


class TestRootRoutes:
    """Tests d'intégration pour les routes racines de l'API"""

    def test_root_endpoint_integration(self):
        """Tester la route racine (/)"""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
        assert "status" in response.json()
        assert response.json()["status"] == "online"
        assert settings.APP_NAME in response.json()["message"]

    def test_status_endpoint_integration(self):
        """Tester la route de statut (/status)"""
        response = client.get("/status")
        assert response.status_code == 200
        assert response.json()["status"] == "online"
        assert "app_name" in response.json()
        assert response.json()["app_name"] == settings.APP_NAME
        assert "version" in response.json()
