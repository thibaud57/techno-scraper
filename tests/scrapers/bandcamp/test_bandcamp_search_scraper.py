from unittest.mock import patch, AsyncMock

import pytest

from app.core.errors import ResourceNotFoundException, ParsingException
from app.models.bandcamp_models import BandcampEntityType
from app.scrapers.bandcamp.bandcamp_search_scraper import BandcampSearchScraper
from tests.mocks.bandcamp_mocks import (
    BANDCAMP_SEARCH_RESPONSE,
    BANDCAMP_EMPTY_RESPONSE,
    BANDCAMP_404_RESPONSE,
    mock_bandcamp_response_factory
)




class TestBandcampSearchScraper:
    
    @pytest.fixture
    def scraper(self):
        return BandcampSearchScraper()
    
    @pytest.mark.asyncio
    @patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock)
    async def test_scrape_successful(self, mock_fetch, scraper, mock_bandcamp_response_factory):
        mock_response = mock_bandcamp_response_factory(html=BANDCAMP_SEARCH_RESPONSE)
        mock_fetch.return_value = mock_response
        
        result = await scraper.scrape("mutual rytm", page=1, entity_type=BandcampEntityType.BANDS)
        
        assert result is not None
        assert len(result.bands) == 2
        
        first_profile = result.bands[0]
        assert first_profile.name == "Mutual Rytm"
        assert "https://mutual-rytm.bandcamp.com" in str(first_profile.url)
        assert first_profile.location == "Germany"
        assert first_profile.genre == "electronic"
        assert str(first_profile.avatar_url) == "https://f4.bcbits.com/img/a123456789_1.jpg"
        
        second_profile = result.bands[1]
        assert second_profile.name == "Test Label"
        assert "https://test-label.bandcamp.com" in str(second_profile.url)
        assert second_profile.location == "France"
        assert second_profile.genre == "techno"

    @pytest.mark.asyncio
    @patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock)
    async def test_scrape_empty_results(self, mock_fetch, scraper, mock_bandcamp_response_factory):
        mock_response = mock_bandcamp_response_factory(html=BANDCAMP_EMPTY_RESPONSE)
        mock_fetch.return_value = mock_response
        
        result = await scraper.scrape("nonexistent", page=1, entity_type=BandcampEntityType.BANDS)
        
        assert result is not None
        assert len(result.bands) == 0

    @pytest.mark.asyncio
    @patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock)
    async def test_scrape_404_error(self, mock_fetch, scraper, mock_bandcamp_response_factory):
        mock_response = mock_bandcamp_response_factory(status_code=404, text=BANDCAMP_404_RESPONSE)
        mock_fetch.return_value = mock_response
        
        with pytest.raises(ResourceNotFoundException) as exc_info:
            await scraper.scrape("invalid_query", page=1, entity_type=BandcampEntityType.BANDS)
        
        assert "Recherche Bandcamp" in str(exc_info.value)
        assert "invalid_query" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock)
    async def test_scrape_parsing_error(self, mock_fetch, scraper, mock_bandcamp_response_factory):
        mock_response = mock_bandcamp_response_factory(html="invalid html")
        mock_fetch.return_value = mock_response
        
        result = await scraper.scrape("test", page=1, entity_type=BandcampEntityType.BANDS)
        
        assert result is not None
        assert len(result.bands) == 0

    @pytest.mark.asyncio
    @patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock)
    async def test_scrape_with_pagination(self, mock_fetch, scraper, mock_bandcamp_response_factory):
        mock_response = mock_bandcamp_response_factory(html=BANDCAMP_SEARCH_RESPONSE)
        mock_fetch.return_value = mock_response
        
        result = await scraper.scrape("test", page=2, entity_type=BandcampEntityType.BANDS)
        
        assert len(result.bands) == 2
        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert call_args[1]['params'] == {'page': 2}

    @pytest.mark.asyncio
    @patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock)
    async def test_scrape_tracks_entity_type(self, mock_fetch, scraper, mock_bandcamp_response_factory):
        mock_response = mock_bandcamp_response_factory(html=BANDCAMP_SEARCH_RESPONSE)
        mock_fetch.return_value = mock_response
        
        result = await scraper.scrape("test", page=1, entity_type=BandcampEntityType.TRACKS)
        
        mock_fetch.assert_called_once()
        call_args = mock_fetch.call_args
        assert "item_type=t" in call_args[0][0]

    def test_parse_search_results_empty(self, scraper):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup("<html></html>", 'html.parser')
        
        profiles = scraper._parse_search_results(soup)
        
        assert profiles == []

    def test_parse_search_results_with_data(self, scraper):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(BANDCAMP_SEARCH_RESPONSE, 'html.parser')
        
        profiles = scraper._parse_search_results(soup)
        
        assert len(profiles) == 2
        assert profiles[0].name == "Mutual Rytm"
        assert profiles[1].name == "Test Label"