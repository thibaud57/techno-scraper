"""
Configuration pour les tests des scrapers.
"""
import pytest
import asyncio
import pytest_asyncio

# Importer les mocks partagés
from tests.mocks.http_mocks import mock_http_response_factory
from tests.mocks.soundcloud_mocks import mock_soundcloud_user_data, mock_soundcloud_search_data, mock_soundcloud_webprofiles_data, mock_social_links

# Rendre les mocks disponibles pour les tests de scrapers
mock_response_factory = mock_http_response_factory 