from unittest.mock import patch

import pytest

from app.models import SocialLink, SoundcloudProfile, SoundcloudSearchResult


@pytest.fixture
def mock_soundcloud_profile_integration():
    """
    Objet profil SoundCloud pour les tests d'intégration
    """
    return SoundcloudProfile(
        id=123456,
        name="Test user integration",
        url="https://soundcloud.com/test_user_integration",
        permalink_url="https://soundcloud.com/test_user_integration",
        description="This is a test bio for integration tests",
        followers_count=1000,
        country_code="FR",
        avatar_url="https://example.com/avatar_integration.jpg"
    )


@pytest.fixture
def mock_soundcloud_search_data_integration():
    """
    Objet de recherche SoundCloud pour les tests d'intégration
    """
    profile1 = SoundcloudProfile(
        id=123,
        name="Test user1 integration",
        url="https://soundcloud.com/test_user1_integration",
        permalink_url="https://soundcloud.com/test_user1_integration",
        description="This is a test bio 1 for integration",
        followers_count=1000,
        country_code="FR",
        avatar_url="https://example.com/avatar1_integration.jpg"
    )

    profile2 = SoundcloudProfile(
        id=456,
        name="Test user2 integration",
        url="https://soundcloud.com/test_user2_integration",
        permalink_url="https://soundcloud.com/test_user2_integration",
        description="This is a test bio 2 for integration",
        followers_count=2000,
        country_code="US",
        avatar_url="https://example.com/avatar2_integration.jpg"
    )

    return SoundcloudSearchResult(
        total=2,
        next_href=None,
        profiles=[profile1, profile2]
    )


@pytest.fixture
def mock_soundcloud_webprofiles_data_integration():
    """
    Données de webprofiles SoundCloud pour les tests d'intégration
    """
    return [
        {
            "url": "https://instagram.com/test_user_integration",
            "network": "instagram"
        },
        {
            "url": "https://facebook.com/test_user_integration",
            "network": "facebook"
        },
        {
            "url": "https://example-integration.com",
            "network": "personal"
        }
    ]


@pytest.fixture
def mock_social_links_integration():
    """
    Liens sociaux pour les tests d'intégration
    """
    return [
        SocialLink(platform="facebook", url="https://facebook.com/test_user_integration"),
        SocialLink(platform="instagram", url="https://instagram.com/test_user_integration"),
        SocialLink(platform="website", url="https://example-integration.com")
    ]


@pytest.fixture
def patch_soundcloud_profile_scraper():
    """
    Patch le scraper de profil SoundCloud pour les tests d'intégration.
    """
    with patch("app.scrapers.SoundcloudProfileScraper.scrape") as mock_scrape:
        yield mock_scrape


@pytest.fixture
def patch_soundcloud_search_scraper():
    """
    Patch le scraper de recherche SoundCloud pour les tests d'intégration.
    """
    with patch("app.scrapers.SoundcloudSearchProfileScraper.scrape") as mock_scrape:
        yield mock_scrape


@pytest.fixture
def patch_soundcloud_webprofiles_scraper():
    """
    Patch le scraper de webprofiles SoundCloud pour les tests d'intégration.
    """
    with patch("app.scrapers.SoundcloudWebprofilesScraper.scrape") as mock_scrape:
        yield mock_scrape
