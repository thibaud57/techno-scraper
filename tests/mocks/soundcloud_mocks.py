import pytest
from unittest.mock import patch

from tests.mocks.http_mocks import mock_http_response_factory

# Réutiliser le mock de réponse HTTP générique
mock_response_factory = mock_http_response_factory


@pytest.fixture
def mock_soundcloud_user_data():
    """
    Données de profil utilisateur SoundCloud pour les tests
    """
    return {
        "kind": "user",
        "id": 123456,
        "username": "test_user",
        "permalink": "test_user",
        "permalink_url": "https://soundcloud.com/test_user",
        "description": "This is a test bio",
        "followers_count": 1000,
        "country_code": "FR",
        "avatar_url": "https://example.com/avatar.jpg"
    }


@pytest.fixture
def mock_soundcloud_search_data():
    """
    Données de recherche SoundCloud pour les tests
    """
    return {
        "total_results": 2,
        "collection": [
            {
                "kind": "user",
                "id": 123,
                "username": "test_user1",
                "permalink": "test_user1",
                "permalink_url": "https://soundcloud.com/test_user1",
                "description": "This is a test bio 1",
                "followers_count": 1000,
                "country_code": "FR",
                "avatar_url": "https://example.com/avatar1.jpg"
            },
            {
                "kind": "user",
                "id": 456,
                "username": "test_user2",
                "permalink": "test_user2",
                "permalink_url": "https://soundcloud.com/test_user2",
                "description": "This is a test bio 2",
                "followers_count": 2000,
                "country_code": "US",
                "avatar_url": "https://example.com/avatar2.jpg"
            }
        ]
    }


@pytest.fixture
def mock_soundcloud_webprofiles_data():
    """
    Données de webprofiles SoundCloud pour les tests
    """
    return [
        {
            "created_at": "2023/10/26 17:50:50 +0000",
            "id": 350958810,
            "kind": "web-profile",
            "service": "instagram",
            "title": "",
            "url": "https://instagram.com/test_user",
            "username": "test_user"
        },
        {
            "created_at": "2023/10/26 17:50:50 +0000",
            "id": 350958811,
            "kind": "web-profile",
            "service": "facebook",
            "title": "",
            "url": "https://facebook.com/test_user",
            "username": "test_user"
        },
        {
            "created_at": "2023/10/26 17:50:50 +0000",
            "id": 350958812,
            "kind": "web-profile",
            "service": "personal",
            "title": "",
            "url": "https://example.com",
            "username": "test_user"
        }
    ]


@pytest.fixture
def mock_soundcloud_credentials():
    """
    Mock pour les identifiants SoundCloud dans les tests.
    Utilisé uniquement quand nécessaire (pas autouse=True).
    """
    with patch('app.core.config.settings.SOUNDCLOUD_CLIENT_ID', 'test_client_id'), \
         patch('app.core.config.settings.SOUNDCLOUD_CLIENT_SECRET', 'test_client_secret'):
        yield


@pytest.fixture(autouse=True)
def mock_soundcloud_auth_service():
    """
    Mock pour le service d'authentification SoundCloud dans les tests
    """
    with patch('app.services.soundcloud.soundcloud_auth.get_access_token',
               return_value="test_access_token"), \
         patch('app.services.soundcloud.soundcloud_auth.build_auth_url',
               side_effect=lambda url: f"{url}?access_token=test_access_token"), \
         patch('app.services.soundcloud.soundcloud_auth.get_auth_headers',
               return_value={"Authorization": "OAuth test_access_token"}):
        yield
