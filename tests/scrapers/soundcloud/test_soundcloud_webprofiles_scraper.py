from unittest.mock import patch, AsyncMock

import pytest

from app.core.errors import ResourceNotFoundException, ParsingException
from app.models import SocialLink
from app.scrapers.soundcloud.soundcloud_webprofiles_scraper import SoundcloudWebprofilesScraper
from tests.mocks.soundcloud_mocks import mock_soundcloud_webprofiles_data


class TestSoundcloudWebprofilesScraper:
    
    @pytest.fixture
    def scraper(self):
        return SoundcloudWebprofilesScraper()
    
    @pytest.mark.asyncio
    @patch('app.services.soundcloud.soundcloud_api_service.SoundcloudApiService.get_user_webprofiles', new_callable=AsyncMock)
    async def test_scrape_success(self, mock_get_user_webprofiles, scraper, mock_soundcloud_webprofiles_data):
        mock_get_user_webprofiles.return_value = mock_soundcloud_webprofiles_data
        
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
    @patch('app.services.soundcloud.soundcloud_api_service.SoundcloudApiService.get_user_webprofiles', new_callable=AsyncMock)
    async def test_scrape_404_error(self, mock_get_user_webprofiles, scraper):
        mock_get_user_webprofiles.side_effect = ResourceNotFoundException(
            resource_type="Webprofiles SoundCloud",
            resource_id="123456",
            details={"user_id": 123456}
        )
        
        with pytest.raises(ResourceNotFoundException) as excinfo:
            await scraper.scrape(123456)
        
        assert "Webprofiles SoundCloud" in str(excinfo.value)
        assert "123456" in str(excinfo.value)
    
    @pytest.mark.asyncio
    @patch('app.services.soundcloud.soundcloud_api_service.SoundcloudApiService.get_user_webprofiles', new_callable=AsyncMock)
    async def test_scrape_invalid_json(self, mock_get_user_webprofiles, scraper):
        mock_get_user_webprofiles.side_effect = ParsingException(
            message="Erreur lors du parsing des réseaux sociaux pour l'ID 123456: Invalid JSON",
            details={"error": "Invalid JSON"}
        )
        
        with pytest.raises(ParsingException) as excinfo:
            await scraper.scrape(123456)
        
        assert "Erreur lors du parsing des réseaux sociaux" in str(excinfo.value)
    
    @pytest.mark.asyncio
    @patch('app.services.soundcloud.soundcloud_api_service.SoundcloudApiService.get_user_webprofiles', new_callable=AsyncMock)
    async def test_scrape_empty_webprofiles(self, mock_get_user_webprofiles, scraper):
        mock_get_user_webprofiles.return_value = []
        
        result = await scraper.scrape(123456)
        
        assert isinstance(result, list)
        assert len(result) == 0