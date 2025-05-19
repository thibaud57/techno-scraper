from unittest.mock import patch, AsyncMock

import pytest

from app.core.errors import ResourceNotFoundException, ParsingException
from app.models import SocialLink
from app.scrapers.soundcloud.soundcloud_webprofiles_scraper import SoundcloudWebprofilesScraper


class TestSoundcloudWebprofilesScraper:
    
    @pytest.fixture
    def scraper(self):
        return SoundcloudWebprofilesScraper()
    
    @pytest.mark.asyncio
    @patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock)
    async def test_scrape_success(self, mock_fetch, scraper, mock_response_factory, mock_soundcloud_webprofiles_data):
        mock_response = mock_response_factory(json_data=mock_soundcloud_webprofiles_data)
        mock_fetch.return_value = mock_response
        
        result = await scraper.scrape(123456)
        
        assert isinstance(result, list)
        assert len(result) == 3
        assert all(isinstance(link, SocialLink) for link in result)
        
        platforms = [link.platform.value for link in result]
        assert "facebook" in platforms
        assert "website" in platforms  # "personal" est converti en "website"
        
        urls = [str(link.url) for link in result]
        assert "https://facebook.com/test_user" in urls
        assert "https://example.com" in urls or "https://example.com/" in urls
    
    @pytest.mark.asyncio
    @patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock)
    async def test_scrape_404_error(self, mock_fetch, scraper, mock_response_factory):
        mock_response = mock_response_factory(status_code=404)
        mock_fetch.return_value = mock_response
        
        with pytest.raises(ResourceNotFoundException) as excinfo:
            await scraper.scrape(123456)
        
        assert "Webprofiles SoundCloud" in str(excinfo.value)
        assert "123456" in str(excinfo.value)
    
    @pytest.mark.asyncio
    @patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock)
    async def test_scrape_invalid_json(self, mock_fetch, scraper, mock_response_factory):
        mock_response = mock_response_factory()
        mock_response.json.side_effect = Exception("Invalid JSON")
        mock_fetch.return_value = mock_response
        
        with pytest.raises(ParsingException) as excinfo:
            await scraper.scrape(123456)
        
        assert "Erreur lors du parsing des réseaux sociaux" in str(excinfo.value)
    
    @pytest.mark.asyncio
    @patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock)
    async def test_scrape_empty_webprofiles(self, mock_fetch, scraper, mock_response_factory):
        mock_response = mock_response_factory(json_data=[])
        mock_fetch.return_value = mock_response
        
        result = await scraper.scrape(123456)
        
        assert isinstance(result, list)
        assert len(result) == 0 