"""
Tests pour le service API SoundCloud.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

import httpx

from app.core.errors import (
    NetworkException,
    PermanentScraperException,
    TemporaryScraperException,
    AuthenticationException,
    RateLimitException
)
from app.services.soundcloud.soundcloud_api_service import SoundcloudApiService


class TestSoundcloudApiService:
    
    @pytest.fixture
    def api_service(self):
        return SoundcloudApiService()
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.request', new_callable=AsyncMock)
    @patch('app.services.soundcloud.soundcloud_auth.get_access_token', new_callable=AsyncMock)
    async def test_fetch_success_with_auth_header(self, mock_get_token, mock_request, api_service):
        # Configurer les mocks
        mock_get_token.return_value = "test_access_token"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_request.return_value = mock_response
        
        # Appeler la méthode à tester
        url = "https://api.soundcloud.com/users/123"
        response = await api_service.fetch(url, use_auth_header=True)
        
        # Vérifier que la méthode request a été appelée avec les bons arguments
        mock_request.assert_called_once()
        call_args = mock_request.call_args[1]
        assert call_args["url"] == url
        assert call_args["headers"]["Authorization"] == "OAuth test_access_token"
        
        # Vérifier que la réponse est correcte
        assert response.status_code == 200
        assert response.json() == {"test": "data"}
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.request', new_callable=AsyncMock)
    @patch('app.services.soundcloud.soundcloud_auth.build_auth_url', new_callable=AsyncMock)
    async def test_fetch_success_with_auth_url(self, mock_build_url, mock_request, api_service):
        # Configurer les mocks
        mock_build_url.return_value = "https://api.soundcloud.com/users/123?client_id=test_client_id"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_request.return_value = mock_response
        
        # Appeler la méthode à tester
        url = "https://api.soundcloud.com/users/123"
        response = await api_service.fetch(url, use_auth_header=False)
        
        # Vérifier que la méthode request a été appelée avec les bons arguments
        mock_request.assert_called_once()
        call_args = mock_request.call_args[1]
        assert call_args["url"] == "https://api.soundcloud.com/users/123?client_id=test_client_id"
        assert "Authorization" not in call_args["headers"]
        
        # Vérifier que la réponse est correcte
        assert response.status_code == 200
        assert response.json() == {"test": "data"}
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.request', new_callable=AsyncMock)
    @patch('app.services.soundcloud.soundcloud_auth.get_access_token', new_callable=AsyncMock)
    async def test_fetch_rate_limit_error(self, mock_get_token, mock_request, api_service):
        # Configurer les mocks
        mock_get_token.return_value = "test_access_token"
        
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60"}
        mock_request.return_value = mock_response
        
        # Vérifier que l'exception est levée
        with pytest.raises(RateLimitException) as excinfo:
            url = "https://api.soundcloud.com/users/123"
            await api_service.fetch(url)
        
        # Vérifier que le message d'erreur est correct
        assert "Limite de taux atteinte" in str(excinfo.value)
        assert excinfo.value.details.get("retry_after") == 60
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.request', new_callable=AsyncMock)
    @patch('app.services.soundcloud.soundcloud_auth.get_access_token', new_callable=AsyncMock)
    async def test_fetch_server_error(self, mock_get_token, mock_request, api_service):
        # Configurer les mocks
        mock_get_token.return_value = "test_access_token"
        
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_request.return_value = mock_response
        
        # Vérifier que l'exception est levée
        with pytest.raises(TemporaryScraperException) as excinfo:
            url = "https://api.soundcloud.com/users/123"
            await api_service.fetch(url)
        
        # Vérifier que le message d'erreur est correct
        assert "Erreur serveur" in str(excinfo.value)
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.request', new_callable=AsyncMock)
    @patch('app.services.soundcloud.soundcloud_auth.get_access_token', new_callable=AsyncMock)
    async def test_fetch_forbidden_error(self, mock_get_token, mock_request, api_service):
        # Configurer les mocks
        mock_get_token.return_value = "test_access_token"
        
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"error": "Forbidden"}
        mock_request.return_value = mock_response
        
        # Vérifier que l'exception est levée
        with pytest.raises(AuthenticationException) as excinfo:
            url = "https://api.soundcloud.com/users/123"
            await api_service.fetch(url)
        
        # Vérifier que le message d'erreur est correct
        assert "Accès interdit" in str(excinfo.value)
        assert excinfo.value.status_code == 401  # AuthenticationException utilise 401
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.request', new_callable=AsyncMock)
    @patch('app.services.soundcloud.soundcloud_auth.get_access_token', new_callable=AsyncMock)
    async def test_fetch_client_error(self, mock_get_token, mock_request, api_service):
        # Configurer les mocks
        mock_get_token.return_value = "test_access_token"
        
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Bad Request"}
        mock_request.return_value = mock_response
        
        # Vérifier que l'exception est levée
        with pytest.raises(PermanentScraperException) as excinfo:
            url = "https://api.soundcloud.com/users/123"
            await api_service.fetch(url)
        
        # Vérifier que le message d'erreur est correct
        assert "Erreur client" in str(excinfo.value)
        assert excinfo.value.status_code == 400
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.request', side_effect=httpx.TimeoutException("Timeout"))
    @patch('app.services.soundcloud.soundcloud_auth.get_access_token', new_callable=AsyncMock)
    async def test_fetch_timeout_error(self, mock_get_token, mock_request, api_service):
        # Configurer les mocks
        mock_get_token.return_value = "test_access_token"
        
        # Vérifier que l'exception est levée
        with pytest.raises(NetworkException) as excinfo:
            url = "https://api.soundcloud.com/users/123"
            await api_service.fetch(url)
        
        # Vérifier que le message d'erreur est correct
        assert "Timeout" in str(excinfo.value)
    
    @pytest.mark.asyncio
    @patch('app.services.soundcloud.soundcloud_api_service.SoundcloudApiService.fetch', new_callable=AsyncMock)
    async def test_search_users(self, mock_fetch, api_service):
        # Configurer le mock
        mock_response = MagicMock()
        mock_response.json.return_value = {"collection": [{"id": 123}], "total_results": 1}
        mock_fetch.return_value = mock_response
        
        # Appeler la méthode à tester
        result = await api_service.search_users("test", 10, 0)
        
        # Vérifier que la méthode fetch a été appelée avec les bons arguments
        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args[0]
        assert "https://api.soundcloud.com/users" in call_args[0]
        assert mock_fetch.call_args[1]["params"]["q"] == "test"
        assert mock_fetch.call_args[1]["params"]["limit"] == 10
        assert mock_fetch.call_args[1]["params"]["offset"] == 0
        
        # Vérifier que le résultat est correct
        assert result["collection"] == [{"id": 123}]
        assert result["total_results"] == 1
    
    @pytest.mark.asyncio
    @patch('app.services.soundcloud.soundcloud_api_service.SoundcloudApiService.fetch', new_callable=AsyncMock)
    async def test_get_user(self, mock_fetch, api_service):
        # Configurer le mock
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 123, "username": "test_user"}
        mock_fetch.return_value = mock_response
        
        # Appeler la méthode à tester
        result = await api_service.get_user(123)
        
        # Vérifier que la méthode fetch a été appelée avec les bons arguments
        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args[0]
        assert "https://api.soundcloud.com/users/123" in call_args[0]
        
        # Vérifier que le résultat est correct
        assert result["id"] == 123
        assert result["username"] == "test_user"
    
    @pytest.mark.asyncio
    @patch('app.services.soundcloud.soundcloud_api_service.SoundcloudApiService.fetch', new_callable=AsyncMock)
    async def test_get_user_webprofiles(self, mock_fetch, api_service):
        # Configurer le mock
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "service": "instagram",
                "url": "https://instagram.com/test_user"
            }
        ]
        mock_fetch.return_value = mock_response
        
        # Appeler la méthode à tester
        result = await api_service.get_user_webprofiles(123)
        
        # Vérifier que la méthode fetch a été appelée avec les bons arguments
        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args[0]
        assert "https://api.soundcloud.com/users/123/web-profiles" in call_args[0]
        
        # Vérifier que le résultat est correct
        assert len(result) == 1
        assert result[0]["service"] == "instagram"
        assert result[0]["url"] == "https://instagram.com/test_user"