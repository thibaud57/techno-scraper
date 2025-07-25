"""
Configuration pour les tests des scrapers.
"""

# Importer les mocks partagés
from tests.mocks.http_mocks import mock_http_response_factory

# Rendre les mocks disponibles pour les tests de scrapers
mock_response_factory = mock_http_response_factory
