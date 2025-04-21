from unittest.mock import patch, AsyncMock

import pytest

from app.core.errors import ResourceNotFoundException, ParsingException
from app.models import SoundcloudSearchResult, LimitEnum, SocialLink
from app.scrapers.soundcloud.soundcloud_search_profile_scraper import SoundcloudSearchProfileScraper
from tests.mocks.soundcloud_mocks import mock_soundcloud_search_data


class TestSoundcloudSearchProfileScraper:
    
    @pytest.mark.asyncio
    @patch('app.scrapers.soundcloud.soundcloud_webprofiles_scraper.SoundcloudWebprofilesScraper.scrape', new_callable=AsyncMock)
    async def test_scrape_success(self, mock_webprofiles_scrape, mock_response_factory, mock_soundcloud_search_data):
        mock_response = mock_response_factory(json_data=mock_soundcloud_search_data)
        
        social_links1 = [SocialLink(platform="instagram", url="https://instagram.com/test_user1")]
        social_links2 = [SocialLink(platform="facebook", url="https://facebook.com/test_user2")]
        
        mock_webprofiles_scrape.side_effect = [social_links1, social_links2]
        
        with patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock, return_value=mock_response):
            scraper = SoundcloudSearchProfileScraper()
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
    async def test_scrape_404_error(self, mock_response_factory):
        mock_response = mock_response_factory(status_code=404)
        
        with patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock, return_value=mock_response):
            scraper = SoundcloudSearchProfileScraper()
            with pytest.raises(ResourceNotFoundException) as excinfo:
                await scraper.scrape("test query")
            
            assert "Recherche de profils Soundcloud" in str(excinfo.value)
            assert "test query" in str(excinfo.value)
    
    @pytest.mark.asyncio
    async def test_scrape_empty_results(self, mock_response_factory):
        mock_response = mock_response_factory(json_data={
            "total_results": 0,
            "collection": []
        })
        
        with patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock, return_value=mock_response):
            scraper = SoundcloudSearchProfileScraper()
            result = await scraper.scrape("test query")
            
            assert isinstance(result, SoundcloudSearchResult)
            assert result.total_results == 0
            assert len(result.profiles) == 0
    
    @pytest.mark.asyncio
    @patch('app.scrapers.soundcloud.soundcloud_webprofiles_scraper.SoundcloudWebprofilesScraper.scrape', new_callable=AsyncMock)
    async def test_scrape_with_webprofiles_error(self, mock_webprofiles_scrape, mock_response_factory, mock_soundcloud_search_data):
        mock_response = mock_response_factory(json_data=mock_soundcloud_search_data)
        # Simuler une erreur lors de la récupération des réseaux sociaux
        mock_webprofiles_scrape.side_effect = Exception("Test error")
        
        with patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock, return_value=mock_response):
            scraper = SoundcloudSearchProfileScraper()
            result = await scraper.scrape("test query")
            
            assert isinstance(result, SoundcloudSearchResult)
            assert len(result.profiles) == 2
            # Tous les profils devraient avoir une liste vide de réseaux sociaux
            assert len(result.profiles[0].social_links) == 0
            assert len(result.profiles[1].social_links) == 0
    
    @pytest.mark.asyncio
    async def test_scrape_invalid_json(self, mock_response_factory):
        mock_response = mock_response_factory()
        mock_response.json.side_effect = Exception("Invalid JSON")
        
        with patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock, return_value=mock_response):
            scraper = SoundcloudSearchProfileScraper()
            with pytest.raises(ParsingException) as excinfo:
                await scraper.scrape("test query")
            
            assert "Erreur lors du parsing" in str(excinfo.value) 