from unittest.mock import MagicMock

import httpx
import pytest


@pytest.fixture
def mock_http_response_factory():
    """
    Factory pour créer des réponses HTTP mock avec différents codes de statut.
    Utilisable par n'importe quel scraper qui utilise httpx.
    """

    def _make_response(status_code=200, json_data=None, headers=None, content=None):
        response = MagicMock(spec=httpx.Response)
        response.status_code = status_code
        response.headers = headers or {}

        if json_data is not None:
            response.json.return_value = json_data

        if content is not None:
            response.content = content

        return response

    return _make_response
