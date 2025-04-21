from unittest.mock import MagicMock, patch

import httpx
import pytest


# Réutiliser la factory de base des tests unitaires

@pytest.fixture
def mock_network_error_integration():
    """
    Crée une exception de réseau httpx à utiliser dans les tests d'intégration.
    """
    return httpx.RequestError("Erreur réseau simulée (intégration)", request=MagicMock())


@pytest.fixture
def patch_httpx_client():
    """
    Fixture pour patcher le client httpx dans les tests d'intégration.
    Permet d'intercepter les appels HTTP dans toute l'application.
    """
    with patch("httpx.AsyncClient") as mock_client:
        instance = mock_client.return_value
        instance.__aenter__.return_value = instance
        yield instance
