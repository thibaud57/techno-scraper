"""
Tests pour le service d'authentification SoundCloud.
"""
from unittest.mock import AsyncMock, patch

import pytest

from app.services.soundcloud.soundcloud_auth_service import \
    SoundcloudAuthService
from tests.mocks.soundcloud_mocks import mock_soundcloud_credentials


class TestSoundcloudAuthService:
    
    @pytest.fixture
    def auth_service(self):
        return SoundcloudAuthService()
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post', new_callable=AsyncMock)
    async def test_get_access_token_success(self, mock_post, auth_service, mock_soundcloud_credentials):
        # Configurer le mock pour simuler une réponse réussie
        mock_response = AsyncMock()
        mock_response.status_code = 200
        # Faire en sorte que json() retourne une valeur directement, pas une coroutine
        mock_response.json = lambda: {
            "access_token": "test_access_token",
            "expires_in": 3600,
            "scope": "",
            "token_type": "bearer"
        }
        mock_post.return_value = mock_response
        
        # Appeler la méthode à tester
        token = await auth_service.get_access_token()
        
        # Vérifier que la méthode post a été appelée avec les bons arguments
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "https://api.soundcloud.com/oauth2/token" in call_args[0][0]  # Premier argument positionnel
        assert call_args[1]["data"]["grant_type"] == "client_credentials"
        # Vérifier que les identifiants sont présents, sans vérifier leurs valeurs exactes
        assert "client_id" in call_args[1]["data"]
        assert "client_secret" in call_args[1]["data"]
        
        # Vérifier que le token est correct
        assert token == "test_access_token"
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post', new_callable=AsyncMock)
    async def test_get_access_token_error(self, mock_post, auth_service, mock_soundcloud_credentials):
        # Configurer le mock pour simuler une erreur
        mock_response = AsyncMock()
        mock_response.status_code = 401
        # Faire en sorte que json() retourne une valeur directement, pas une coroutine
        mock_response.json = lambda: {
            "error": "invalid_client",
            "error_description": "Invalid client credentials"
        }
        mock_post.return_value = mock_response
        
        # Vérifier que l'exception est levée
        with pytest.raises(Exception) as excinfo:
            await auth_service.get_access_token()
        
        # Vérifier que le message d'erreur est correct
        assert "Erreur" in str(excinfo.value) and "authentification SoundCloud" in str(excinfo.value)
    
    @pytest.mark.asyncio
    async def test_build_auth_url(self, auth_service):
        # Patcher get_access_token pour retourner un token connu
        with patch.object(auth_service, 'get_access_token', return_value="test_access_token"):
            # Appeler la méthode à tester
            url = "https://api.soundcloud.com/users/123"
            auth_url = await auth_service.build_auth_url(url)
            
            # Vérifier que l'URL est correcte
            assert auth_url == "https://api.soundcloud.com/users/123?access_token=test_access_token"
    
    @pytest.mark.asyncio
    async def test_get_auth_headers(self, auth_service):
        # Patcher get_access_token pour retourner un token connu
        with patch.object(auth_service, 'get_access_token', return_value="test_access_token"):
            # Appeler la méthode à tester
            headers = await auth_service.get_auth_headers()
            
            # Vérifier que les headers sont corrects
            assert headers == {"Authorization": "OAuth test_access_token"}