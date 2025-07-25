from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.errors import ResourceNotFoundException, ParsingException, ScraperException
from app.main import app
from tests.integration.mocks import (
    mock_soundcloud_search_data_integration,
    mock_social_links_integration,
    mock_soundcloud_profile_integration,
    patch_soundcloud_profile_scraper,
    patch_soundcloud_search_scraper,
    patch_soundcloud_webprofiles_scraper
)

# Client de test pour les appels API
client = TestClient(app)

# Headers avec une clé API valide pour les tests
API_HEADERS = {"X-API-Key": settings.API_KEY}
INVALID_API_HEADERS = {"X-API-Key": "invalid-key"}
NO_API_HEADERS = {}


class TestSoundcloudRoutes:
    """Tests d'intégration pour les routes Soundcloud"""

    def test_search_profiles_unauthorized_integration(self):
        """Test d'intégration: recherche de profils sans clé API valide"""
        response = client.get("/api/soundcloud/search-profile/test", headers=NO_API_HEADERS)
        assert response.status_code == 403

        response = client.get("/api/soundcloud/search-profile/test", headers=INVALID_API_HEADERS)
        assert response.status_code == 403

    def test_search_profiles_success_integration(self, patch_soundcloud_search_scraper,
                                                 mock_soundcloud_search_data_integration):
        """Test d'intégration: recherche de profils avec succès"""
        patch_soundcloud_search_scraper.return_value = mock_soundcloud_search_data_integration

        response = client.get("/api/soundcloud/search-profile/test_user", headers=API_HEADERS)
        assert response.status_code == 200

        data = response.json()
        assert "profiles" in data
        assert len(data["profiles"]) == 2
        assert data["profiles"][0]["id"] == 123
        assert data["profiles"][1]["id"] == 456
        assert data["profiles"][0]["name"] == "Test user1 integration"

    def test_search_profiles_not_found_integration(self, patch_soundcloud_search_scraper):
        """Test d'intégration: recherche de profils non trouvés"""
        patch_soundcloud_search_scraper.side_effect = ResourceNotFoundException(
            resource_type="Profil SoundCloud",
            resource_id="non_existant"
        )

        response = client.get("/api/soundcloud/search-profile/non_existant", headers=API_HEADERS)
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "non trouvé" in data["detail"].lower()

    def test_search_profiles_parsing_error_integration(self, patch_soundcloud_search_scraper):
        """Test d'intégration: erreur de parsing lors de la recherche de profils"""
        patch_soundcloud_search_scraper.side_effect = ParsingException("Erreur de parsing")

        response = client.get("/api/soundcloud/search-profile/test", headers=API_HEADERS)
        assert response.status_code == 500

        data = response.json()
        assert "detail" in data
        assert "erreur de parsing" in data["detail"].lower()

    def test_search_profiles_unexpected_error_integration(self, patch_soundcloud_search_scraper):
        """Test d'intégration: erreur inattendue lors de la recherche de profils"""
        patch_soundcloud_search_scraper.side_effect = Exception("Erreur inattendue")

        response = client.get("/api/soundcloud/search-profile/test", headers=API_HEADERS)
        assert response.status_code == 500

        data = response.json()
        assert "detail" in data
        assert "erreur inattendue" in data["detail"].lower()

    def test_get_profile_success_integration(self, patch_soundcloud_profile_scraper,
                                             mock_soundcloud_profile_integration):
        """Test d'intégration: récupération d'un profil avec succès"""
        patch_soundcloud_profile_scraper.return_value = mock_soundcloud_profile_integration

        response = client.get("/api/soundcloud/profile/123456", headers=API_HEADERS)
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == 123456
        assert data["name"] == "Test user integration"
        assert data["url"] == "https://soundcloud.com/test_user_integration"

    def test_get_profile_not_found_integration(self, patch_soundcloud_profile_scraper):
        """Test d'intégration: profil non trouvé"""
        patch_soundcloud_profile_scraper.side_effect = ResourceNotFoundException(
            resource_type="Profil SoundCloud",
            resource_id="999999"
        )

        response = client.get("/api/soundcloud/profile/999999", headers=API_HEADERS)
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "non trouvé" in data["detail"].lower()

    def test_get_profile_parsing_error_integration(self, patch_soundcloud_profile_scraper):
        """Test d'intégration: erreur de parsing lors de la récupération d'un profil"""
        patch_soundcloud_profile_scraper.side_effect = ParsingException("Erreur de parsing")

        response = client.get("/api/soundcloud/profile/123456", headers=API_HEADERS)
        assert response.status_code == 500

        data = response.json()
        assert "detail" in data
        assert "erreur de parsing" in data["detail"].lower()

    def test_get_profile_unexpected_error_integration(self, patch_soundcloud_profile_scraper):
        """Test d'intégration: erreur inattendue lors de la récupération d'un profil"""
        patch_soundcloud_profile_scraper.side_effect = Exception("Erreur inattendue")

        response = client.get("/api/soundcloud/profile/123456", headers=API_HEADERS)
        assert response.status_code == 500

        data = response.json()
        assert "detail" in data
        assert "erreur inattendue" in data["detail"].lower()

    def test_get_webprofiles_success_integration(self, patch_soundcloud_webprofiles_scraper,
                                                 mock_social_links_integration):
        """Test d'intégration: récupération des liens sociaux avec succès"""
        patch_soundcloud_webprofiles_scraper.return_value = mock_social_links_integration

        response = client.get("/api/soundcloud/profile/123456/webprofiles", headers=API_HEADERS)
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 3
        assert any(link["platform"] == "facebook" for link in data)
        assert any(link["platform"] == "instagram" for link in data)
        assert any(link["platform"] == "website" for link in data)
        assert any(link["url"] == "https://facebook.com/test_user_integration" for link in data)

    def test_get_webprofiles_not_found_integration(self, patch_soundcloud_webprofiles_scraper):
        """Test d'intégration: liens sociaux non trouvés"""
        patch_soundcloud_webprofiles_scraper.side_effect = ResourceNotFoundException(
            resource_type="Profil SoundCloud",
            resource_id="999999"
        )

        response = client.get("/api/soundcloud/profile/999999/webprofiles", headers=API_HEADERS)
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "non trouvé" in data["detail"].lower()

    def test_get_webprofiles_parsing_error_integration(self, patch_soundcloud_webprofiles_scraper):
        """Test d'intégration: erreur de parsing lors de la récupération des liens sociaux"""
        patch_soundcloud_webprofiles_scraper.side_effect = ParsingException("Erreur de parsing")

        response = client.get("/api/soundcloud/profile/123456/webprofiles", headers=API_HEADERS)
        assert response.status_code == 500

        data = response.json()
        assert "detail" in data
        assert "erreur de parsing" in data["detail"].lower()

    def test_get_webprofiles_error_integration(self, patch_soundcloud_webprofiles_scraper):
        """Test d'intégration: erreur lors de la récupération des liens sociaux"""
        patch_soundcloud_webprofiles_scraper.side_effect = ScraperException("Erreur de scraping", 500)

        response = client.get("/api/soundcloud/profile/123456/webprofiles", headers=API_HEADERS)
        assert response.status_code == 500

        data = response.json()
        assert "detail" in data
        assert "erreur de scraping" in data["detail"].lower()

    def test_get_webprofiles_unexpected_error_integration(self, patch_soundcloud_webprofiles_scraper):
        """Test d'intégration: erreur inattendue lors de la récupération des liens sociaux"""
        patch_soundcloud_webprofiles_scraper.side_effect = Exception("Erreur inattendue")

        response = client.get("/api/soundcloud/profile/123456/webprofiles", headers=API_HEADERS)
        assert response.status_code == 500

        data = response.json()
        assert "detail" in data
        assert "erreur inattendue" in data["detail"].lower()
