from unittest.mock import patch, AsyncMock

import pytest

from app.core.errors import ResourceNotFoundException, ParsingException
from app.models import SoundcloudSearchResult, LimitEnum, SocialLink
from app.scrapers.soundcloud.soundcloud_search_profile_scraper import SoundcloudSearchProfileScraper
from tests.mocks.soundcloud_mocks import mock_soundcloud_search_data


class TestSoundcloudSearchProfileScraper:
    
    @pytest.fixture
    def scraper(self):
        """Fixture pour créer une instance du scraper"""
        return SoundcloudSearchProfileScraper()
    
    @pytest.mark.asyncio
    @patch('app.scrapers.soundcloud.soundcloud_webprofiles_scraper.SoundcloudWebprofilesScraper.scrape', new_callable=AsyncMock)
    @patch('app.services.soundcloud.soundcloud_api_service.SoundcloudApiService.search_users', new_callable=AsyncMock)
    async def test_scrape_success(self, mock_search_users, mock_webprofiles_scrape, scraper, mock_soundcloud_search_data):
        mock_search_users.return_value = mock_soundcloud_search_data
        
        social_links1 = [SocialLink(platform="instagram", url="https://instagram.com/test_user1")]
        social_links2 = [SocialLink(platform="facebook", url="https://facebook.com/test_user2")]
        
        mock_webprofiles_scrape.side_effect = [social_links1, social_links2]
        
        result = await scraper.scrape("test query", page=1, limit=LimitEnum.TEN)
        
        assert isinstance(result, SoundcloudSearchResult)
        assert result.total_results == 2
        assert result.page == 1
        assert result.limit == LimitEnum.TEN
        assert len(result.profiles) == 2
        
        assert result.profiles[0].id == 123
        assert result.profiles[0].name == "test_user1"
        assert len(result.profiles[0].social_links) == 1
        assert result.profiles[0].social_links[0].platform.value == "instagram"
        
        assert result.profiles[1].id == 456
        assert result.profiles[1].name == "test_user2"
        assert len(result.profiles[1].social_links) == 1
        assert result.profiles[1].social_links[0].platform.value == "facebook"
    
    @pytest.mark.asyncio
    @patch('app.services.soundcloud.soundcloud_api_service.SoundcloudApiService.search_users', new_callable=AsyncMock)
    async def test_scrape_404_error(self, mock_search_users, scraper):
        mock_search_users.side_effect = ResourceNotFoundException(
            resource_type="Recherche de profils Soundcloud",
            resource_id="test query",
            details={"query": "test query"}
        )
        
        with pytest.raises(ResourceNotFoundException) as excinfo:
            await scraper.scrape("test query")
        
        assert "Recherche de profils Soundcloud" in str(excinfo.value)
        assert "test query" in str(excinfo.value)
    
    @pytest.mark.asyncio
    @patch('app.services.soundcloud.soundcloud_api_service.SoundcloudApiService.search_users', new_callable=AsyncMock)
    async def test_scrape_empty_results(self, mock_search_users, scraper):
        mock_search_users.return_value = {
            "total_results": 0,
            "collection": []
        }
        
        result = await scraper.scrape("test query")
        
        assert isinstance(result, SoundcloudSearchResult)
        assert result.total_results == 0
        assert len(result.profiles) == 0
    
    @pytest.mark.asyncio
    @patch('app.scrapers.soundcloud.soundcloud_webprofiles_scraper.SoundcloudWebprofilesScraper.scrape', new_callable=AsyncMock)
    @patch('app.services.soundcloud.soundcloud_api_service.SoundcloudApiService.search_users', new_callable=AsyncMock)
    async def test_scrape_with_webprofiles_error(self, mock_search_users, mock_webprofiles_scrape, scraper, mock_soundcloud_search_data):
        mock_search_users.return_value = mock_soundcloud_search_data
        # Simuler une erreur lors de la récupération des réseaux sociaux
        mock_webprofiles_scrape.side_effect = Exception("Test error")
        
        result = await scraper.scrape("test query")
        
        assert isinstance(result, SoundcloudSearchResult)
        assert len(result.profiles) == 2
        # Tous les profils devraient avoir une liste vide de réseaux sociaux
        assert len(result.profiles[0].social_links) == 0
        assert len(result.profiles[1].social_links) == 0
    
    @pytest.mark.asyncio
    @patch('app.services.soundcloud.soundcloud_api_service.SoundcloudApiService.search_users', new_callable=AsyncMock)
    async def test_scrape_invalid_json(self, mock_search_users, scraper):
        mock_search_users.side_effect = ParsingException(
            message="Erreur lors du parsing de la recherche pour 'test query': Invalid JSON",
            details={"error": "Invalid JSON"}
        )
        
        with pytest.raises(ParsingException) as excinfo:
            await scraper.scrape("test query")
        
        assert "Erreur lors du parsing" in str(excinfo.value)