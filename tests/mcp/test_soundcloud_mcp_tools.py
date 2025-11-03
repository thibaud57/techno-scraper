import pytest
from unittest.mock import AsyncMock, patch

from app.mcp.tools.soundcloud_tools import (
    execute_soundcloud_search,
    execute_soundcloud_get_profile,
)
from app.models import SoundcloudSearchResult, SoundcloudProfile, LimitEnum


class TestSoundcloudMcpTools:

    @pytest.mark.asyncio
    @patch('app.mcp.tools.soundcloud_tools.SoundcloudSearchProfileScraper')
    async def test_execute_soundcloud_search_success(self, mock_scraper_class):
        mock_profile = SoundcloudProfile(
            id=123,
            name="Test Artist",
            url="https://soundcloud.com/test-artist",
            bio="Test bio",
            location="Test Location",
            followers_count=1000,
            social_links=[]
        )

        mock_result = SoundcloudSearchResult(
            total_results=1,
            page=1,
            limit=LimitEnum.TEN,
            profiles=[mock_profile]
        )

        mock_scraper = AsyncMock()
        mock_scraper.scrape.return_value = mock_result
        mock_scraper_class.return_value = mock_scraper

        result = await execute_soundcloud_search(query="test", page=1, limit=10)

        assert "total_results" in result
        assert result["total_results"] == 1
        assert "profiles" in result
        assert len(result["profiles"]) == 1
        assert result["profiles"][0]["name"] == "Test Artist"
        mock_scraper.scrape.assert_called_once_with(name="test", page=1, limit=LimitEnum.TEN)

    @pytest.mark.asyncio
    @patch('app.mcp.tools.soundcloud_tools.SoundcloudSearchProfileScraper')
    async def test_execute_soundcloud_search_with_limit_20(self, mock_scraper_class):
        mock_result = SoundcloudSearchResult(
            total_results=0,
            page=1,
            limit=LimitEnum.TWENTY,
            profiles=[]
        )

        mock_scraper = AsyncMock()
        mock_scraper.scrape.return_value = mock_result
        mock_scraper_class.return_value = mock_scraper

        result = await execute_soundcloud_search(query="test", page=1, limit=20)

        mock_scraper.scrape.assert_called_once_with(name="test", page=1, limit=LimitEnum.TWENTY)

    @pytest.mark.asyncio
    @patch('app.mcp.tools.soundcloud_tools.SoundcloudSearchProfileScraper')
    async def test_execute_soundcloud_search_error(self, mock_scraper_class):
        mock_scraper = AsyncMock()
        mock_scraper.scrape.side_effect = Exception("Test error")
        mock_scraper_class.return_value = mock_scraper

        result = await execute_soundcloud_search(query="test", page=1, limit=10)

        assert "error" in result
        assert result["error"] == "Test error"
        assert result["tool"] == "soundcloud_search_profiles"
        assert result["query"] == "test"

    @pytest.mark.asyncio
    @patch('app.mcp.tools.soundcloud_tools.SoundcloudProfileScraper')
    async def test_execute_soundcloud_get_profile_success(self, mock_scraper_class):
        mock_profile = SoundcloudProfile(
            id=123456,
            name="Test Artist",
            url="https://soundcloud.com/test-artist",
            bio="Test bio",
            location="Test Location",
            followers_count=5000,
            social_links=[]
        )

        mock_scraper = AsyncMock()
        mock_scraper.scrape.return_value = mock_profile
        mock_scraper_class.return_value = mock_scraper

        result = await execute_soundcloud_get_profile(user_id=123456)

        assert "id" in result
        assert result["id"] == 123456
        assert result["name"] == "Test Artist"
        assert result["followers_count"] == 5000
        mock_scraper.scrape.assert_called_once_with(user_id=123456)

    @pytest.mark.asyncio
    @patch('app.mcp.tools.soundcloud_tools.SoundcloudProfileScraper')
    async def test_execute_soundcloud_get_profile_error(self, mock_scraper_class):
        mock_scraper = AsyncMock()
        mock_scraper.scrape.side_effect = Exception("Profile not found")
        mock_scraper_class.return_value = mock_scraper

        result = await execute_soundcloud_get_profile(user_id=999999)

        assert "error" in result
        assert result["error"] == "Profile not found"
        assert result["tool"] == "soundcloud_get_profile"
        assert result["user_id"] == 999999
