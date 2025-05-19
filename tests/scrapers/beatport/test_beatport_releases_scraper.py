from datetime import date
from unittest.mock import patch, AsyncMock

import pytest

from app.core.errors import ResourceNotFoundException, ParsingException
from app.models import LimitEnum
from app.models.beatport_models import BeatportEntityType
from app.scrapers.beatport.beatport_releases_scraper import BeatportReleasesScraper
from tests.mocks.beatport_mocks import (
    BEATPORT_ARTIST_RELEASES_RESPONSE,
    BEATPORT_LABEL_RELEASES_RESPONSE,
    BEATPORT_404_RESPONSE,
)


class TestBeatportReleasesScraper:

    @pytest.fixture
    def scraper(self):
        return BeatportReleasesScraper()

    @pytest.mark.asyncio
    @patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock)
    async def test_scrape_artist_releases_success(self, mock_fetch, scraper, mock_beatport_response_factory):
        mock_response = mock_beatport_response_factory(html=BEATPORT_ARTIST_RELEASES_RESPONSE)
        mock_fetch.return_value = mock_response
        
        results = await scraper.scrape(
            entity_type=BeatportEntityType.ARTIST,
            entity_slug="test-artist",
            entity_id="654321",
            page=1,
            limit=LimitEnum.TEN
        )

        # Vérifier que la méthode fetch a été appelée avec la bonne URL
        fetch_call = mock_fetch.call_args_list[0][0][0]
        assert "artist/test-artist/654321/releases" in fetch_call
        assert "page=1" in fetch_call
        assert "per_page=10" in fetch_call

        # Vérifier les résultats
        assert len(results) == 1
        release = results[0]
        assert release.id == 123456
        assert release.title == "Test Release 1"
        assert release.release_date == "2025-01-15"
        assert release.track_count == 3
        assert len(release.artists) == 1
        assert release.artists[0].name == "Test Artist"
        assert release.label.name == "Test Label"

    @pytest.mark.asyncio
    @patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock)
    async def test_scrape_label_releases_success(self, mock_fetch, scraper, mock_beatport_response_factory):
        mock_response = mock_beatport_response_factory(html=BEATPORT_LABEL_RELEASES_RESPONSE)
        mock_fetch.return_value = mock_response
        
        results = await scraper.scrape(
            entity_type=BeatportEntityType.LABEL,
            entity_slug="test-label",
            entity_id="555666",
            page=1,
            limit=LimitEnum.TEN
        )

        # Vérifier que la méthode fetch a été appelée avec la bonne URL
        fetch_call = mock_fetch.call_args_list[0][0][0]
        assert "label/test-label/555666/releases" in fetch_call
        assert "page=1" in fetch_call
        assert "per_page=10" in fetch_call

        # Vérifier les résultats
        assert len(results) == 1
        release = results[0]
        assert release.id == 654321
        assert release.title == "Test Release 2"
        assert release.release_date == "2025-02-20"
        assert release.track_count == 2
        assert len(release.artists) == 1
        assert release.artists[0].name == "Another Artist"
        assert release.label.name == "Test Label"

    @pytest.mark.asyncio
    @patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock)
    async def test_scrape_releases_with_date_filter(self, mock_fetch, scraper, mock_beatport_response_factory):
        # Configurer le mock pour retourner une réponse simulée
        mock_response = mock_beatport_response_factory(html=BEATPORT_ARTIST_RELEASES_RESPONSE)
        mock_fetch.return_value = mock_response
        
        # Définir des dates de filtre
        start_date = date(2025, 1, 1)
        end_date = date(2025, 12, 31)

        # Appeler la méthode scrape avec des dates
        await scraper.scrape(
            entity_type=BeatportEntityType.ARTIST,
            entity_slug="test-artist",
            entity_id="654321",
            page=1,
            limit=LimitEnum.TEN,
            start_date=start_date,
            end_date=end_date
        )

        # Vérifier que la méthode fetch a été appelée avec la bonne URL incluant les dates
        fetch_call = mock_fetch.call_args_list[0][0][0]
        assert "page=1" in fetch_call
        assert "per_page=10" in fetch_call
        # Tenir compte de l'encodage URL (: devient %3A)
        assert "publish_date=2025-01-01%3A2025-12-31" in fetch_call

    @pytest.mark.asyncio
    @patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock)
    async def test_scrape_releases_resource_not_found(self, mock_fetch, scraper, mock_beatport_response_factory):
        # Configurer le mock pour retourner une réponse 404
        mock_response = mock_beatport_response_factory(status_code=404, text=BEATPORT_404_RESPONSE)
        mock_fetch.return_value = mock_response
        
        # Vérifier que l'exception ResourceNotFoundException est levée
        with pytest.raises(ResourceNotFoundException):
            await scraper.scrape(
                entity_type=BeatportEntityType.ARTIST,
                entity_slug="nonexistent-artist",
                entity_id="999999",
                page=1,
                limit=LimitEnum.TEN
            )

    @pytest.mark.asyncio
    @patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock)
    async def test_scrape_releases_parsing_error(self, mock_fetch, scraper, mock_beatport_response_factory):
        # Configurer le mock pour retourner une réponse avec un JSON invalide
        mock_response = mock_beatport_response_factory(
            html="<script id='__NEXT_DATA__' type='application/json'>Invalid JSON</script>"
        )
        mock_fetch.return_value = mock_response
        
        # Vérifier que l'exception ParsingException est levée
        with pytest.raises(ParsingException):
            await scraper.scrape(
                entity_type=BeatportEntityType.ARTIST,
                entity_slug="test-artist",
                entity_id="654321",
                page=1,
                limit=LimitEnum.TEN
            )

    @pytest.mark.asyncio
    @patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock)
    async def test_build_releases_url(self, mock_fetch, scraper, mock_beatport_response_factory):
        # Configurer le mock pour éviter les appels réseau réels
        mock_response = mock_beatport_response_factory(html=BEATPORT_ARTIST_RELEASES_RESPONSE)
        mock_fetch.return_value = mock_response
        
        # Test avec un artiste
        await scraper.scrape(
            entity_type=BeatportEntityType.ARTIST,
            entity_slug="test-artist",
            entity_id="123456",
            page=1,
            limit=LimitEnum.TEN
        )
        artist_url = mock_fetch.call_args_list[0][0][0]
        assert "artist/test-artist/123456/releases" in artist_url
        
        # Réinitialiser le mock
        mock_fetch.reset_mock()
        
        # Test avec un label
        await scraper.scrape(
            entity_type=BeatportEntityType.LABEL,
            entity_slug="test-label",
            entity_id="789012",
            page=1,
            limit=LimitEnum.TEN
        )
        label_url = mock_fetch.call_args_list[0][0][0]
        assert "label/test-label/789012/releases" in label_url 