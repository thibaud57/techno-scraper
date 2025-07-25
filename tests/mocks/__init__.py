"""
Mocks et fixtures pour les tests
"""

# Import des fixtures SoundCloud
from .soundcloud_mocks import (
    mock_soundcloud_user_data,
    mock_soundcloud_search_data,
    mock_soundcloud_webprofiles_data,
    mock_soundcloud_credentials,
    mock_soundcloud_auth_service,
    mock_response_factory
)

# Import des fixtures Beatport
from .beatport_mocks import (
    mock_beatport_response_factory,
    mock_beatport_artist_data,
    mock_beatport_label_data,
    mock_beatport_release_data,
    mock_beatport_specific_format_release_data
)

# Import des fixtures HTTP génériques
from .http_mocks import (
    mock_http_response_factory
)

__all__ = [
    # SoundCloud
    'mock_soundcloud_user_data',
    'mock_soundcloud_search_data',
    'mock_soundcloud_webprofiles_data',
    'mock_soundcloud_credentials',
    'mock_soundcloud_auth_service',
    'mock_response_factory',
    
    # Beatport
    'mock_beatport_response_factory',
    'mock_beatport_artist_data',
    'mock_beatport_label_data',
    'mock_beatport_release_data',
    'mock_beatport_specific_format_release_data',
    
    # HTTP
    'mock_http_response_factory'
]