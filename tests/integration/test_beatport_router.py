from fastapi.testclient import TestClient
from datetime import date

from app.core.config import settings
from app.core.errors import ResourceNotFoundException, ParsingException, ScraperException
from app.main import app
from app.models.beatport_models import BeatportEntityType, BeatportReleaseEntityType
from app.models.pagination_models import LimitEnum
from tests.integration.mocks import (
    mock_beatport_search_result_integration,
    mock_beatport_empty_search_result_integration,
    mock_beatport_releases_integration,
    patch_beatport_search_scraper,
    patch_beatport_releases_scraper
)

# Client de test pour les appels API
client = TestClient(app)

# Headers avec une clé API valide pour les tests
API_HEADERS = {"X-API-Key": settings.API_KEY}
INVALID_API_HEADERS = {"X-API-Key": "invalid-key"}
NO_API_HEADERS = {}


class TestBeatportRoutes:
    """Tests d'intégration pour les routes Beatport"""

    def test_search_unauthorized_integration(self):
        """Test d'intégration: recherche sans clé API valide"""
        response = client.get("/api/beatport/search/test", headers=NO_API_HEADERS)
        assert response.status_code == 403

        response = client.get("/api/beatport/search/test", headers=INVALID_API_HEADERS)
        assert response.status_code == 403

    def test_search_success_integration(self, patch_beatport_search_scraper,
                                        mock_beatport_search_result_integration):
        """Test d'intégration: recherche avec succès"""
        patch_beatport_search_scraper.return_value = mock_beatport_search_result_integration

        response = client.get("/api/beatport/search/test_query", headers=API_HEADERS)
        assert response.status_code == 200

        data = response.json()
        assert "tracks" in data
        assert "artists" in data
        assert "labels" in data
        assert len(data["tracks"]) == 2
        assert len(data["artists"]) == 2
        assert len(data["labels"]) == 1
        assert data["tracks"][0]["id"] == 12345
        assert data["tracks"][0]["title"] == "Test Track 1"
        assert data["page"] == 2

    def test_search_with_entity_type_integration(self, patch_beatport_search_scraper,
                                                 mock_beatport_search_result_integration):
        """Test d'intégration: recherche avec type d'entité"""
        patch_beatport_search_scraper.return_value = mock_beatport_search_result_integration

        response = client.get("/api/beatport/search/test_query?entity_type=track", headers=API_HEADERS)
        assert response.status_code == 200

        # Vérifier que le scraper a été appelé (les arguments seront vérifiés par FastAPI)
        patch_beatport_search_scraper.assert_called_once()

    def test_search_with_pagination_integration(self, patch_beatport_search_scraper,
                                                mock_beatport_search_result_integration):
        """Test d'intégration: recherche avec pagination"""
        patch_beatport_search_scraper.return_value = mock_beatport_search_result_integration

        response = client.get("/api/beatport/search/test_query?page=2&limit=25", headers=API_HEADERS)
        assert response.status_code == 200

        # Vérifier que le scraper a été appelé (les arguments seront vérifiés par FastAPI)
        patch_beatport_search_scraper.assert_called_once()

    def test_search_empty_results_integration(self, patch_beatport_search_scraper,
                                              mock_beatport_empty_search_result_integration):
        """Test d'intégration: recherche sans résultats"""
        patch_beatport_search_scraper.return_value = mock_beatport_empty_search_result_integration

        response = client.get("/api/beatport/search/no_results", headers=API_HEADERS)
        assert response.status_code == 200

        data = response.json()
        assert len(data["tracks"]) == 0
        assert len(data["artists"]) == 0
        assert len(data["labels"]) == 0
        assert data["page"] == 1
        assert data["total_results"] == 0

    def test_search_not_found_integration(self, patch_beatport_search_scraper):
        """Test d'intégration: recherche non trouvée"""
        patch_beatport_search_scraper.side_effect = ResourceNotFoundException(
            resource_type="Recherche Beatport",
            resource_id="non_existant"
        )

        response = client.get("/api/beatport/search/non_existant", headers=API_HEADERS)
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "non trouvé" in data["detail"].lower()

    def test_search_parsing_error_integration(self, patch_beatport_search_scraper):
        """Test d'intégration: erreur de parsing lors de la recherche"""
        patch_beatport_search_scraper.side_effect = ParsingException("Erreur de parsing")

        response = client.get("/api/beatport/search/test", headers=API_HEADERS)
        assert response.status_code == 500

        data = response.json()
        assert "detail" in data
        assert "erreur de parsing" in data["detail"].lower()

    def test_search_scraper_error_integration(self, patch_beatport_search_scraper):
        """Test d'intégration: erreur de scraper lors de la recherche"""
        patch_beatport_search_scraper.side_effect = ScraperException("Erreur de scraping", 503)

        response = client.get("/api/beatport/search/test", headers=API_HEADERS)
        assert response.status_code == 503

        data = response.json()
        assert "detail" in data
        assert "erreur de scraping" in data["detail"].lower()

    def test_search_unexpected_error_integration(self, patch_beatport_search_scraper):
        """Test d'intégration: erreur inattendue lors de la recherche"""
        patch_beatport_search_scraper.side_effect = Exception("Erreur inattendue")

        response = client.get("/api/beatport/search/test", headers=API_HEADERS)
        assert response.status_code == 500

        data = response.json()
        assert "detail" in data
        assert "erreur inattendue" in data["detail"].lower()

    def test_get_releases_unauthorized_integration(self):
        """Test d'intégration: récupération des releases sans clé API valide"""
        response = client.get("/api/beatport/artist/test-artist/releases?entity_id=123", headers=NO_API_HEADERS)
        assert response.status_code == 403

        response = client.get("/api/beatport/artist/test-artist/releases?entity_id=123", headers=INVALID_API_HEADERS)
        assert response.status_code == 403

    def test_get_releases_success_integration(self, patch_beatport_releases_scraper,
                                              mock_beatport_releases_integration):
        """Test d'intégration: récupération des releases avec succès"""
        patch_beatport_releases_scraper.return_value = mock_beatport_releases_integration

        response = client.get("/api/beatport/artist/test-artist/releases?entity_id=123", headers=API_HEADERS)
        assert response.status_code == 200

        data = response.json()
        assert "releases" in data
        assert "facets" in data
        assert len(data["releases"]) == 2
        assert data["releases"][0]["id"] == 12345
        assert data["releases"][0]["title"] == "Test Release 1"
        assert data["releases"][0]["track_count"] == 5
        assert data["releases"][1]["id"] == 67890
        assert data["releases"][1]["label"]["name"] == "Test Label 2"

    def test_get_releases_with_pagination_and_dates_integration(self, patch_beatport_releases_scraper,
                                                                mock_beatport_releases_integration):
        """Test d'intégration: récupération des releases avec pagination et dates"""
        patch_beatport_releases_scraper.return_value = mock_beatport_releases_integration

        url = "/api/beatport/artist/test-artist/releases?entity_id=123&page=2&limit=25"
        url += "&start_date=2023-01-01&end_date=2023-12-31"
        response = client.get(url, headers=API_HEADERS)
        assert response.status_code == 200

        # Vérifier que le scraper a été appelé (les arguments seront vérifiés par FastAPI)
        patch_beatport_releases_scraper.assert_called_once()

    def test_get_label_releases_success_integration(self, patch_beatport_releases_scraper,
                                                   mock_beatport_releases_integration):
        """Test d'intégration: récupération des releases d'un label avec succès"""
        patch_beatport_releases_scraper.return_value = mock_beatport_releases_integration

        response = client.get("/api/beatport/label/test-label/releases?entity_id=456", headers=API_HEADERS)
        assert response.status_code == 200

        # Vérifier que le scraper a été appelé (les arguments seront vérifiés par FastAPI)
        patch_beatport_releases_scraper.assert_called_once()

    def test_get_releases_not_found_integration(self, patch_beatport_releases_scraper):
        """Test d'intégration: releases non trouvées"""
        patch_beatport_releases_scraper.side_effect = ResourceNotFoundException(
            resource_type="Releases Beatport",
            resource_id="non_existant"
        )

        response = client.get("/api/beatport/artist/non-existant/releases?entity_id=999", headers=API_HEADERS)
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "non trouvé" in data["detail"].lower()

    def test_get_releases_parsing_error_integration(self, patch_beatport_releases_scraper):
        """Test d'intégration: erreur de parsing lors de la récupération des releases"""
        patch_beatport_releases_scraper.side_effect = ParsingException("Erreur de parsing")

        response = client.get("/api/beatport/artist/test-artist/releases?entity_id=123", headers=API_HEADERS)
        assert response.status_code == 500

        data = response.json()
        assert "detail" in data
        assert "erreur de parsing" in data["detail"].lower()

    def test_get_releases_scraper_error_integration(self, patch_beatport_releases_scraper):
        """Test d'intégration: erreur de scraper lors de la récupération des releases"""
        patch_beatport_releases_scraper.side_effect = ScraperException("Erreur de scraping", 503)

        response = client.get("/api/beatport/artist/test-artist/releases?entity_id=123", headers=API_HEADERS)
        assert response.status_code == 503

        data = response.json()
        assert "detail" in data
        assert "erreur de scraping" in data["detail"].lower()

    def test_get_releases_unexpected_error_integration(self, patch_beatport_releases_scraper):
        """Test d'intégration: erreur inattendue lors de la récupération des releases"""
        patch_beatport_releases_scraper.side_effect = Exception("Erreur inattendue")

        response = client.get("/api/beatport/artist/test-artist/releases?entity_id=123", headers=API_HEADERS)
        assert response.status_code == 500

        data = response.json()
        assert "detail" in data
        assert "erreur inattendue" in data["detail"].lower() 