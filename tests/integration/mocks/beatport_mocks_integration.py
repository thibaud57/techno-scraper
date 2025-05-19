from unittest.mock import patch

import pytest
from datetime import date
from app.models import Release, Track, BeatportSearchResult, ArtistProfile
from app.models.beatport_models import BeatportEntityType
from app.models.pagination_models import LimitEnum


@pytest.fixture
def mock_beatport_search_result_integration():
    """
    Objet de résultat de recherche Beatport pour les tests d'intégration
    """
    track1 = Track(
        id=12345,
        title="Test Track 1",
        url="https://www.beatport.com/track/test-track-1/12345",
        duration=360,
        label=ArtistProfile(
            id=7890,
            name="Test Label 1",
            url="https://www.beatport.com/label/test-label-1/7890"
        ),
        release_date="2023-01-15",
        artists=[
            ArtistProfile(
                id=1111,
                name="Test Artist 1",
                url="https://www.beatport.com/artist/test-artist-1/1111"
            )
        ],
        remixers=[
            ArtistProfile(
                id=2222,
                name="Test Remixer 1",
                url="https://www.beatport.com/artist/test-remixer-1/2222"
            )
        ],
        artwork_url="https://example.com/artwork1.jpg"
    )

    track2 = Track(
        id=67890,
        title="Test Track 2",
        url="https://www.beatport.com/track/test-track-2/67890",
        duration=420,
        label=ArtistProfile(
            id=8901,
            name="Test Label 2",
            url="https://www.beatport.com/label/test-label-2/8901"
        ),
        release_date="2023-02-20",
        artists=[
            ArtistProfile(
                id=3333,
                name="Test Artist 2",
                url="https://www.beatport.com/artist/test-artist-2/3333"
            )
        ],
        remixers=[],
        artwork_url="https://example.com/artwork2.jpg"
    )

    artist1 = ArtistProfile(
        id=1111,
        name="Test Artist 1",
        url="https://www.beatport.com/artist/test-artist-1/1111"
    )

    artist2 = ArtistProfile(
        id=3333,
        name="Test Artist 2",
        url="https://www.beatport.com/artist/test-artist-2/3333"
    )

    label1 = ArtistProfile(
        id=7890,
        name="Test Label 1",
        url="https://www.beatport.com/label/test-label-1/7890"
    )

    return BeatportSearchResult(
        tracks=[track1, track2],
        artists=[artist1, artist2],
        labels=[label1],
        total_results=5,
        page=2,
        limit=LimitEnum.TEN
    )


@pytest.fixture
def mock_beatport_empty_search_result_integration():
    """
    Objet de résultat de recherche Beatport vide pour les tests d'intégration
    """
    return BeatportSearchResult(
        tracks=[],
        artists=[],
        labels=[],
        total_results=0,
        page=1,
        limit=LimitEnum.TEN
    )


@pytest.fixture
def mock_beatport_releases_integration():
    """
    Liste de releases Beatport pour les tests d'intégration
    """
    release1 = Release(
        id=12345,
        title="Test Release 1",
        url="https://www.beatport.com/release/test-release-1/12345",
        release_date="2023-01-15",
        label=ArtistProfile(
            id=7890,
            name="Test Label 1",
            url="https://www.beatport.com/label/test-label-1/7890"
        ),
        artists=[
            ArtistProfile(
                id=1111,
                name="Test Artist 1",
                url="https://www.beatport.com/artist/test-artist-1/1111"
            )
        ],
        artwork_url="https://example.com/release_artwork1.jpg",
        track_count=5
    )

    release2 = Release(
        id=67890,
        title="Test Release 2",
        url="https://www.beatport.com/release/test-release-2/67890",
        release_date="2023-02-20",
        label=ArtistProfile(
            id=8901,
            name="Test Label 2",
            url="https://www.beatport.com/label/test-label-2/8901"
        ),
        artists=[
            ArtistProfile(
                id=3333,
                name="Test Artist 2",
                url="https://www.beatport.com/artist/test-artist-2/3333"
            )
        ],
        artwork_url="https://example.com/release_artwork2.jpg",
        track_count=3
    )

    return [release1, release2]


@pytest.fixture
def patch_beatport_search_scraper():
    """
    Patch le scraper de recherche Beatport pour les tests d'intégration.
    """
    with patch("app.scrapers.BeatportSearchScraper.scrape") as mock_scrape:
        yield mock_scrape


@pytest.fixture
def patch_beatport_releases_scraper():
    """
    Patch le scraper de releases Beatport pour les tests d'intégration.
    """
    with patch("app.scrapers.BeatportReleasesScraper.scrape") as mock_scrape:
        yield mock_scrape 