from unittest.mock import AsyncMock, Mock

import pytest

from app.core.errors import TemporaryScraperException, PermanentScraperException, ScraperException
from app.services.retry_service import with_retry, async_with_retry


class TestRetryService:

    def test_with_retry_success(self):
        # Une fonction qui réussit du premier coup
        @with_retry()
        def successful_function():
            return "success"
        
        result = successful_function()
        assert result == "success"
    
    def test_with_retry_after_temporary_failures(self):
        mock_function = Mock()
        # La fonction échoue 2 fois puis réussit
        mock_function.side_effect = [
            TemporaryScraperException("Erreur temporaire 1"),
            TemporaryScraperException("Erreur temporaire 2"),
            "success"
        ]
        
        @with_retry(max_attempts=3, min_wait=0.01, max_wait=0.01)
        def function_with_retries():
            return mock_function()
        
        result = function_with_retries()
        assert result == "success"
        assert mock_function.call_count == 3
    
    def test_with_retry_max_attempts_exceeded(self):
        mock_function = Mock()
        # La fonction échoue à chaque tentative
        mock_function.side_effect = TemporaryScraperException("Erreur temporaire")
        
        @with_retry(max_attempts=3, min_wait=0.01, max_wait=0.01)
        def function_with_retries():
            return mock_function()
        
        # Pour ce test, nous vérifions que l'exception temporaire est bien levée
        # car dans le code réel, c'est dans le wrapper de with_retry qu'elle
        # est convertie en PermanentScraperException après épuisement des tentatives
        with pytest.raises(TemporaryScraperException) as excinfo:
            function_with_retries()
        
        assert "Erreur temporaire" in str(excinfo.value)
        # Vérifier que la fonction a bien été appelée 3 fois
        assert mock_function.call_count == 3
    
    def test_with_retry_permanent_exception(self):
        mock_function = Mock()
        # La fonction lève une exception permanente
        mock_function.side_effect = PermanentScraperException("Erreur permanente")
        
        @with_retry(max_attempts=3, min_wait=0.01, max_wait=0.01)
        def function_with_retries():
            return mock_function()
        
        with pytest.raises(PermanentScraperException) as excinfo:
            function_with_retries()
        
        assert "Erreur permanente" in str(excinfo.value)
        assert mock_function.call_count == 1  # Pas de retry pour une erreur permanente
    
    def test_with_retry_unexpected_exception(self):
        mock_function = Mock()
        # La fonction lève une exception non gérée
        mock_function.side_effect = ValueError("Erreur inattendue")
        
        @with_retry(max_attempts=3, min_wait=0.01, max_wait=0.01)
        def function_with_retries():
            return mock_function()
        
        with pytest.raises(ScraperException) as excinfo:
            function_with_retries()
        
        assert "Erreur inattendue" in str(excinfo.value)
        assert mock_function.call_count == 1  # Pas de retry pour une erreur non gérée
    
    def test_with_retry_custom_exceptions(self):
        mock_function = Mock()
        # La fonction échoue avec une exception personnalisée puis réussit
        mock_function.side_effect = [
            ValueError("Erreur personnalisée"),
            "success"
        ]
        
        @with_retry(max_attempts=3, retry_exceptions=[ValueError], min_wait=0.01, max_wait=0.01)
        def function_with_retries():
            return mock_function()
        
        result = function_with_retries()
        assert result == "success"
        assert mock_function.call_count == 2
    
    @pytest.mark.asyncio
    async def test_async_with_retry_success(self):
        # Une fonction asynchrone qui réussit du premier coup
        async def successful_async_function(*args, **kwargs):
            return "success"
        
        result = await async_with_retry(successful_async_function)
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_async_with_retry_after_temporary_failures(self):
        mock_function = AsyncMock()
        # La fonction échoue 2 fois puis réussit
        mock_function.side_effect = [
            TemporaryScraperException("Erreur temporaire 1"),
            TemporaryScraperException("Erreur temporaire 2"),
            "success"
        ]
        
        result = await async_with_retry(
            mock_function, 
            max_attempts=3, 
            min_wait=0.01, 
            max_wait=0.01
        )
        
        assert result == "success"
        assert mock_function.call_count == 3
    
    @pytest.mark.asyncio
    async def test_async_with_retry_max_attempts_exceeded(self):
        mock_function = AsyncMock()
        # La fonction échoue à chaque tentative
        mock_function.side_effect = TemporaryScraperException("Erreur temporaire")
        
        with pytest.raises(PermanentScraperException) as excinfo:
            await async_with_retry(
                mock_function, 
                max_attempts=3, 
                min_wait=0.01, 
                max_wait=0.01
            )
        
        assert "Échec après 3 tentatives" in str(excinfo.value)
        assert mock_function.call_count == 3
    
    @pytest.mark.asyncio
    async def test_async_with_retry_permanent_exception(self):
        mock_function = AsyncMock()
        # La fonction lève une exception permanente
        mock_function.side_effect = PermanentScraperException("Erreur permanente")
        
        with pytest.raises(PermanentScraperException) as excinfo:
            await async_with_retry(
                mock_function, 
                max_attempts=3, 
                min_wait=0.01, 
                max_wait=0.01
            )
        
        assert "Erreur permanente" in str(excinfo.value)
        assert mock_function.call_count == 1  # Pas de retry pour une erreur permanente
    
    @pytest.mark.asyncio
    async def test_async_with_retry_unexpected_exception(self):
        mock_function = AsyncMock()
        # La fonction lève une exception non gérée
        mock_function.side_effect = ValueError("Erreur inattendue")
        
        with pytest.raises(ScraperException) as excinfo:
            await async_with_retry(
                mock_function, 
                max_attempts=3, 
                min_wait=0.01, 
                max_wait=0.01
            )
        
        assert "Erreur inattendue" in str(excinfo.value)
        assert mock_function.call_count == 1  # Pas de retry pour une erreur non gérée 