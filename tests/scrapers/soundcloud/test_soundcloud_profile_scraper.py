from unittest.mock import patch, AsyncMock

import pytest

from app.core.errors import ResourceNotFoundException, ParsingException
from app.models import SocialLink, SoundcloudProfile
from app.scrapers.soundcloud.soundcloud_profile_scraper import SoundcloudProfileScraper


class TestSoundcloudProfileScraper:
    
    @pytest.fixture
    def scraper(self):
        return SoundcloudProfileScraper()
    
    @pytest.mark.asyncio
    @patch('app.scrapers.soundcloud.soundcloud_webprofiles_scraper.SoundcloudWebprofilesScraper.scrape', new_callable=AsyncMock)
    @patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock)
    async def test_scrape_success(self, mock_fetch, mock_webprofiles_scrape, scraper, mock_soundcloud_user_data, mock_response_factory):
        mock_response = mock_response_factory(json_data=mock_soundcloud_user_data)
        mock_fetch.return_value = mock_response
        
        social_links = [
            SocialLink(platform="instagram", url="https://instagram.com/test_user")
        ]
        mock_webprofiles_scrape.return_value = social_links
        
        result = await scraper.scrape(123456)
        
        assert isinstance(result, SoundcloudProfile)
        assert result.id == 123456
        assert result.name == "test_user"
        assert str(result.url) == "https://soundcloud.com/test_user"
        assert result.bio == "This is a test bio"
        assert result.followers_count == 1000
        assert result.location == "France"
        assert str(result.avatar_url) == "https://example.com/avatar.jpg"
        assert len(result.social_links) == 1
        assert result.social_links[0].platform.value == "instagram"
        assert str(result.social_links[0].url) == "https://instagram.com/test_user"
    
    @pytest.mark.asyncio
    @patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock)
    async def test_scrape_404_error(self, mock_fetch, scraper, mock_response_factory):
        mock_response = mock_response_factory(status_code=404)
        mock_fetch.return_value = mock_response
        
        with pytest.raises(ResourceNotFoundException) as excinfo:
            await scraper.scrape(123456)
        
        assert "Profil Soundcloud" in str(excinfo.value)
        assert "123456" in str(excinfo.value)
    
    @pytest.mark.asyncio
    @patch('app.scrapers.soundcloud.soundcloud_webprofiles_scraper.SoundcloudWebprofilesScraper.scrape', new_callable=AsyncMock)
    @patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock)
    async def test_scrape_wrong_kind(self, mock_fetch, mock_webprofiles_scrape, scraper, mock_response_factory):
        mock_response = mock_response_factory(json_data={"kind": "track", "id": 123456})
        mock_fetch.return_value = mock_response
        
        mock_webprofiles_scrape.return_value = []
        
        with pytest.raises(ParsingException) as excinfo:
            await scraper.scrape(123456)
        
        assert "n'est pas un profil utilisateur" in str(excinfo.value)
    
    @pytest.mark.asyncio
    @patch('app.scrapers.soundcloud.soundcloud_webprofiles_scraper.SoundcloudWebprofilesScraper.scrape', new_callable=AsyncMock)
    @patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock)
    async def test_scrape_with_webprofiles_error(self, mock_fetch, mock_webprofiles_scrape, scraper, mock_soundcloud_user_data, mock_response_factory):
        mock_response = mock_response_factory(json_data=mock_soundcloud_user_data)
        mock_fetch.return_value = mock_response
        
        mock_webprofiles_scrape.side_effect = Exception("Test error")
        
        result = await scraper.scrape(123456)
        
        assert isinstance(result, SoundcloudProfile)
        assert len(result.social_links) == 0 