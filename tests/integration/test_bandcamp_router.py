from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.errors import ResourceNotFoundException, ParsingException, ScraperException
from app.main import app
from app.models.bandcamp_models import BandcampEntityType
from tests.integration.mocks import (
    mock_bandcamp_search_result_integration,
    mock_bandcamp_empty_search_result_integration,
    patch_bandcamp_search_scraper
)

client = TestClient(app)

API_HEADERS = {"X-API-Key": settings.API_KEY}
INVALID_API_HEADERS = {"X-API-Key": "invalid-key"}
NO_API_HEADERS = {}


class TestBandcampRoutes:
    """Tests d'intégration pour les routes Bandcamp"""

    def test_search_unauthorized_integration(self):
        """Test d'intégration: recherche sans clé API valide"""
        response = client.get("/api/bandcamp/search?query=test", headers=NO_API_HEADERS)
        assert response.status_code == 403

        response = client.get("/api/bandcamp/search?query=test", headers=INVALID_API_HEADERS)
        assert response.status_code == 403

    def test_search_success_integration(self, patch_bandcamp_search_scraper,
                                        mock_bandcamp_search_result_integration):
        """Test d'intégration: recherche avec succès"""
        patch_bandcamp_search_scraper.return_value = mock_bandcamp_search_result_integration

        response = client.get("/api/bandcamp/search?query=test_query", headers=API_HEADERS)
        assert response.status_code == 200

        data = response.json()
        assert "bands" in data
        assert len(data["bands"]) == 2
        assert data["bands"][0]["name"] == "Test Artist Integration"
        assert data["bands"][1]["name"] == "Test Label Integration"

    def test_search_not_found_integration(self, patch_bandcamp_search_scraper):
        """Test d'intégration: recherche qui retourne 404"""
        patch_bandcamp_search_scraper.side_effect = ResourceNotFoundException(
            resource_type="Recherche Bandcamp",
            resource_id="nonexistent_query"
        )

        response = client.get("/api/bandcamp/search?query=nonexistent_query", headers=API_HEADERS)
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "Recherche Bandcamp" in data["detail"]

    def test_search_empty_results_integration(self, patch_bandcamp_search_scraper,
                                              mock_bandcamp_empty_search_result_integration):
        """Test d'intégration: recherche qui retourne des résultats vides"""
        patch_bandcamp_search_scraper.return_value = mock_bandcamp_empty_search_result_integration

        response = client.get("/api/bandcamp/search?query=empty_query", headers=API_HEADERS)
        assert response.status_code == 200

        data = response.json()
        assert "bands" in data
        assert len(data["bands"]) == 0

    def test_search_with_pagination_integration(self, patch_bandcamp_search_scraper,
                                                mock_bandcamp_search_result_integration):
        """Test d'intégration: recherche avec pagination"""
        patch_bandcamp_search_scraper.return_value = mock_bandcamp_search_result_integration

        response = client.get("/api/bandcamp/search?query=test&page=2", headers=API_HEADERS)
        assert response.status_code == 200

        data = response.json()
        assert "bands" in data
        assert len(data["bands"]) == 2

        patch_bandcamp_search_scraper.assert_called_once()
        call_args = patch_bandcamp_search_scraper.call_args
        assert call_args[0][0] == "test"
        assert call_args[0][1] == 2

    def test_search_with_entity_type_integration(self, patch_bandcamp_search_scraper,
                                                 mock_bandcamp_search_result_integration):
        """Test d'intégration: recherche avec type d'entité spécifique"""
        patch_bandcamp_search_scraper.return_value = mock_bandcamp_search_result_integration

        response = client.get("/api/bandcamp/search?query=test&entity_type=t", headers=API_HEADERS)
        assert response.status_code == 200

        data = response.json()
        assert "bands" in data

        patch_bandcamp_search_scraper.assert_called_once()
        call_args = patch_bandcamp_search_scraper.call_args
        assert call_args[0][2] == BandcampEntityType.TRACKS

    def test_search_server_error_integration(self, patch_bandcamp_search_scraper):
        """Test d'intégration: erreur serveur lors de la recherche"""
        patch_bandcamp_search_scraper.side_effect = ScraperException("Erreur serveur")

        response = client.get("/api/bandcamp/search?query=server_error", headers=API_HEADERS)
        assert response.status_code == 500

        data = response.json()
        assert "detail" in data
        assert "Erreur serveur" in data["detail"]

    def test_search_parsing_error_integration(self, patch_bandcamp_search_scraper):
        """Test d'intégration: erreur de parsing lors de la recherche"""
        patch_bandcamp_search_scraper.side_effect = ParsingException("Erreur de parsing")

        response = client.get("/api/bandcamp/search?query=parsing_error", headers=API_HEADERS)
        assert response.status_code == 500

        data = response.json()
        assert "detail" in data
        assert "Erreur de parsing" in data["detail"]