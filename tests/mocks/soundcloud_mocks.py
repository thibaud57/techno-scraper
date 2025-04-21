import pytest

from app.models import SocialLink
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
            "url": "https://instagram.com/test_user",
            "network": "instagram"
        },
        {
            "url": "https://facebook.com/test_user",
            "network": "facebook"
        },
        {
            "url": "https://example.com",
            "network": "personal"
        }
    ]


@pytest.fixture
def mock_social_links():
    """
    Liens sociaux pour les tests
    """
    return [
        SocialLink(platform="facebook", url="https://facebook.com/test_user"),
        SocialLink(platform="instagram", url="https://instagram.com/test_user"),
        SocialLink(platform="website", url="https://example.com")
    ]
