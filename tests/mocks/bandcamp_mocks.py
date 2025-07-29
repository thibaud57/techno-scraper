import pytest
from unittest.mock import MagicMock
from httpx import Response

from tests.mocks.http_mocks import mock_http_response_factory

mock_response_factory = mock_http_response_factory


BANDCAMP_SEARCH_RESPONSE = """
<html>
    <div class="results">
        <li class="searchresult">
            <div class="art">
                <img src="https://f4.bcbits.com/img/a123456789_1.jpg" alt="avatar">
            </div>
            <div class="heading">
                <a href="https://mutual-rytm.bandcamp.com">Mutual Rytm</a>
            </div>
            <div class="subhead">Berlin, Germany</div>
            <div class="genre">electronic</div>
        </li>
        <li class="searchresult">
            <div class="art">
                <img src="https://f4.bcbits.com/img/a987654321_1.jpg" alt="avatar">
            </div>
            <div class="heading">
                <a href="https://test-label.bandcamp.com">Test Label</a>
            </div>
            <div class="subhead">Paris, France</div>
            <div class="genre">techno</div>
        </li>
    </div>
</html>
"""

BANDCAMP_EMPTY_RESPONSE = """
<html>
    <div class="results"></div>
</html>
"""

BANDCAMP_404_RESPONSE = "Not Found"


@pytest.fixture
def mock_bandcamp_response_factory():
    """Factory pour créer des réponses HTTPX mock pour les tests Bandcamp"""
    
    def _create_response(status_code=200, text=None, html=None):
        response = MagicMock()
        response.status_code = status_code
        response.text = html or text or ""
        return response
    
    return _create_response


@pytest.fixture  
def mock_bandcamp_search_data():
    """Données de recherche Bandcamp mockées pour les tests"""
    return {
        "bands": [
            {
                "name": "Mutual Rytm",
                "url": "https://mutual-rytm.bandcamp.com",
                "location": "Germany", 
                "genre": "electronic",
                "avatar_url": "https://f4.bcbits.com/img/a123456789_1.jpg"
            },
            {
                "name": "Test Label",
                "url": "https://test-label.bandcamp.com", 
                "location": "France",
                "genre": "techno",
                "avatar_url": "https://f4.bcbits.com/img/a987654321_1.jpg"
            }
        ]
    }


@pytest.fixture
def mock_bandcamp_profile_data():
    """Données de profil Bandcamp mockées pour les tests"""
    return {
        "name": "Test Artist",
        "url": "https://test-artist.bandcamp.com",
        "location": "Berlin, Germany",
        "genre": "electronic",
        "avatar_url": "https://f4.bcbits.com/img/test_avatar.jpg",
        "bio": "Test artist bio description"
    }