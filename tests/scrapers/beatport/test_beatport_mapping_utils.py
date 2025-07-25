from app.models.beatport_models import BeatportEntityType
from app.scrapers.beatport.beatport_mapping_utils import BeatportMappingUtils
from tests.mocks.beatport_mocks import mock_beatport_release_data, mock_beatport_specific_format_release_data


class TestBeatportMappingUtils:

    def test_build_url(self):
        artist_url = BeatportMappingUtils.build_url(BeatportEntityType.ARTIST, "test-artist", 123456)
        assert artist_url == "https://www.beatport.com/artist/test-artist/123456"

        label_url = BeatportMappingUtils.build_url(BeatportEntityType.LABEL, "test-label", 789012)
        assert label_url == "https://www.beatport.com/label/test-label/789012"

        release_url = BeatportMappingUtils.build_url(BeatportEntityType.RELEASE, "test-release", 456789)
        assert release_url == "https://www.beatport.com/release/test-release/456789"

        search_url = BeatportMappingUtils.build_url(BeatportEntityType.SEARCH, "test query")
        assert search_url == "https://www.beatport.com/search?q=test%20query"

    def test_extract_release_format(self, mock_beatport_release_data):
        release = BeatportMappingUtils.extract_release(mock_beatport_release_data)

        assert release.id == 123456
        assert release.title == "Test Release 1"
        assert str(release.url) == "https://www.beatport.com/release/test-release-1/123456"
        assert release.release_date == "2025-01-15"
        assert release.track_count == 3
        assert len(release.artists) == 1
        assert release.artists[0].id == 654321
        assert release.artists[0].name == "Test Artist"
        assert release.label.id == 555666
        assert release.label.name == "Test Label"

    def test_extract_release_specific_format(self, mock_beatport_specific_format_release_data):
        release = BeatportMappingUtils.extract_release(mock_beatport_specific_format_release_data)

        assert release.id == 123456
        assert release.title == "Test Release 1"
        assert str(release.url) == "https://www.beatport.com/release/test-release-1/123456"
        assert release.release_date == "2025-01-15"
        assert release.track_count == 3
        assert len(release.artists) == 1
        assert release.artists[0].id == 654321
        assert release.artists[0].name == "Test Artist"
        assert release.label.id == 555666
        assert release.label.name == "Test Label"
