"""
Configuration pour les tests des scrapers.
"""
import pytest
import asyncio
import pytest_asyncio

# Importer les mocks partagés
from tests.mocks.http_mocks import mock_http_response_factory
from tests.mocks.soundcloud_mocks import mock_soundcloud_user_data, mock_soundcloud_search_data, mock_soundcloud_webprofiles_data, mock_social_links
from tests.mocks.beatport_mocks import (
    mock_beatport_response_factory,
    mock_beatport_artist_data,
    mock_beatport_label_data,
    mock_beatport_release_data,
    mock_beatport_specific_format_release_data,
    BEATPORT_SEARCH_RESPONSE_IMPROVED,
    BEATPORT_ARTIST_RELEASES_RESPONSE,
    BEATPORT_LABEL_RELEASES_RESPONSE,
    BEATPORT_404_RESPONSE
)

# Rendre les mocks disponibles pour les tests de scrapers
mock_response_factory = mock_http_response_factory