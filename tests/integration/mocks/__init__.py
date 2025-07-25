"""
Mocks et fixtures pour les tests d'intégration
"""

# Import des fixtures Beatport pour l'intégration
from .beatport_mocks_integration import (
    mock_beatport_search_result_integration,
    mock_beatport_empty_search_result_integration,
    mock_beatport_releases_integration,
    patch_beatport_search_scraper,
    patch_beatport_releases_scraper
)

# Import des fixtures SoundCloud pour l'intégration
from .soundcloud_mocks_integration import (
    mock_soundcloud_profile_integration,
    mock_soundcloud_search_data_integration,
    mock_social_links_integration,
    patch_soundcloud_profile_scraper,
    patch_soundcloud_search_scraper,
    patch_soundcloud_webprofiles_scraper
)

__all__ = [
    # Beatport
    'mock_beatport_search_result_integration',
    'mock_beatport_empty_search_result_integration',
    'mock_beatport_releases_integration',
    'patch_beatport_search_scraper',
    'patch_beatport_releases_scraper',
    
    # SoundCloud
    'mock_soundcloud_profile_integration',
    'mock_soundcloud_search_data_integration',
    'mock_social_links_integration',
    'patch_soundcloud_profile_scraper',
    'patch_soundcloud_search_scraper',
    'patch_soundcloud_webprofiles_scraper'
]
