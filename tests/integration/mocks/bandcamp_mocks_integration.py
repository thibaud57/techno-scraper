from unittest.mock import patch

import pytest

from app.models.bandcamp_models import BandcampBandProfile, BandcampSearchResult


@pytest.fixture
def mock_bandcamp_search_result_integration():
    """
    Objet de résultat de recherche Bandcamp pour les tests d'intégration
    """
    profile1 = BandcampBandProfile(
        id=12345,
        name="Test Artist Integration",
        url="https://test-artist-integration.bandcamp.com",
        location="Berlin, Germany",
        genre="electronic",
        avatar_url="https://f4.bcbits.com/img/test_integration_1.jpg"
    )
    
    profile2 = BandcampBandProfile(
        id=67890,
        name="Test Label Integration", 
        url="https://test-label-integration.bandcamp.com",
        location="Paris, France",
        genre="techno",
        avatar_url="https://f4.bcbits.com/img/test_integration_2.jpg"
    )
    
    return BandcampSearchResult(bands=[profile1, profile2])


@pytest.fixture
def mock_bandcamp_empty_search_result_integration():
    """
    Résultat de recherche Bandcamp vide pour les tests d'intégration
    """
    return BandcampSearchResult(bands=[])


@pytest.fixture
def patch_bandcamp_search_scraper():
    """
    Patch pour le scraper de recherche Bandcamp dans les tests d'intégration
    """
    with patch('app.scrapers.bandcamp.bandcamp_search_scraper.BandcampSearchScraper.scrape') as mock:
        yield mock