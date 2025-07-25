from unittest.mock import patch, AsyncMock

import pytest

from app.core.errors import ResourceNotFoundException, ParsingException
from app.models import LimitEnum
from app.models.beatport_models import BeatportEntityType
from app.scrapers.beatport.beatport_search_scraper import BeatportSearchScraper
from tests.mocks.beatport_mocks import (
    BEATPORT_SEARCH_RESPONSE,
    BEATPORT_404_RESPONSE,
    mock_beatport_response_factory
)


class TestBeatportSearchScraper:
    @pytest.fixture
    def scraper(self):
        """Fixture pour créer une instance du scraper"""
        return BeatportSearchScraper()

    @pytest.mark.asyncio
    @patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock)
    async def test_scrape_search_success(self, mock_fetch, scraper, mock_beatport_response_factory):
        mock_response = mock_beatport_response_factory(html=BEATPORT_SEARCH_RESPONSE)
        mock_fetch.return_value = mock_response
        
        # Appeler la méthode scrape
        results = await scraper.scrape(
            query="test query",
            page=1,
            limit=LimitEnum.TEN
        )

        # Vérifier que la méthode fetch a été appelée avec la bonne URL
        fetch_call = mock_fetch.call_args_list[0][0][0]
        assert "search?q=test%20query" in fetch_call

        # Vérifier les résultats
        assert results.total_results > 0
        
        # Vérifier qu'il y a au moins un artiste et un label dans les résultats
        assert len(results.artists) > 0
        assert results.artists[0].name == "Test Artist"
        assert len(results.labels) > 0
        assert results.labels[0].name == "Test Label"
        
        # Vérifier les releases et tracks
        if len(results.releases) > 0:
            assert results.releases[0].title == "Test Release 1"
        
        if len(results.tracks) > 0:
            # Vérifier que le nom de piste a été correctement mappé au titre
            assert hasattr(results.tracks[0], 'title')

    @pytest.mark.asyncio
    @patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock)
    async def test_scrape_search_with_entity_filter(self, mock_fetch, scraper, mock_beatport_response_factory):
        mock_response = mock_beatport_response_factory(html=BEATPORT_SEARCH_RESPONSE)
        mock_fetch.return_value = mock_response
        
        # Appeler la méthode scrape avec un filtre sur les artistes
        results = await scraper.scrape(
            query="test query",
            page=1,
            limit=LimitEnum.TEN,
            entity_type_filter=BeatportEntityType.ARTIST
        )

        # Vérifier que les résultats ne contiennent que des artistes
        assert len(results.artists) > 0
        assert len(results.labels) == 0
        assert len(results.tracks) == 0
        assert len(results.releases) == 0

    @pytest.mark.asyncio
    @patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock)
    async def test_scrape_search_resource_not_found(self, mock_fetch, scraper, mock_beatport_response_factory):
        # Configurer le mock pour retourner une réponse 404
        mock_response = mock_beatport_response_factory(status_code=404, text=BEATPORT_404_RESPONSE)
        mock_fetch.return_value = mock_response
        
        # Vérifier que l'exception ResourceNotFoundException est levée
        with pytest.raises(ResourceNotFoundException):
            await scraper.scrape(
                query="nonexistent query",
                page=1,
                limit=LimitEnum.TEN
            )

    @pytest.mark.asyncio
    @patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock)
    async def test_scrape_search_parsing_error(self, mock_fetch, scraper, mock_beatport_response_factory):
        # Configurer le mock pour retourner une réponse avec un JSON invalide
        mock_response = mock_beatport_response_factory(
            html="<script id='__NEXT_DATA__' type='application/json'>Invalid JSON</script>"
        )
        mock_fetch.return_value = mock_response
        
        # Vérifier que l'exception ParsingException est levée
        with pytest.raises(ParsingException):
            await scraper.scrape(
                query="test query",
                page=1,
                limit=LimitEnum.TEN
            )

    @pytest.mark.asyncio
    @patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock)
    async def test_scrape_search_empty_results(self, mock_fetch, scraper, mock_beatport_response_factory):
        # Créer une réponse avec structure valide mais pas de résultats
        empty_response = """
        <script id="__NEXT_DATA__" type="application/json">
        {
          "props": {
            "pageProps": {
              "dehydratedState": {
                "queries": [
                  {
                    "state": {
                      "data": {
                        "artists": {"data": []},
                        "tracks": {"data": []},
                        "releases": {"data": []},
                        "labels": {"data": []}
                      }
                    },
                    "queryKey": ["search"]
                  }
                ]
              }
            }
          }
        }
        </script>
        """
        
        mock_response = mock_beatport_response_factory(html=empty_response)
        mock_fetch.return_value = mock_response
        
        # Appeler la méthode scrape
        results = await scraper.scrape(
            query="no results query",
            page=1,
            limit=LimitEnum.TEN
        )

        # Vérifier que les résultats sont vides
        assert results.total_results == 0
        assert len(results.artists) == 0
        assert len(results.labels) == 0
        assert len(results.tracks) == 0
        assert len(results.releases) == 0

    @pytest.mark.asyncio
    async def test_extract_next_data_not_found(self, scraper):
        # HTML sans script NEXT_DATA
        html_content = "<html><body>No script here</body></html>"
        
        # Vérifier que l'extraction retourne un dictionnaire vide
        result = scraper._extract_next_data(html_content)
        assert result == {} 