from unittest.mock import patch

from app.models import SoundcloudProfile, SocialLink
from app.scrapers.soundcloud.soundcloud_mapping_utils import SOUNDCLOUD_BASE_URL, \
    SoundcloudMappingUtils
from tests.mocks.soundcloud_mocks import mock_soundcloud_webprofiles_data


class TestSoundcloudMappingUtils:

    def test_build_profile(self):
        user_data = {
            "id": 123456,
            "username": "test_user",
            "permalink_url": "https://soundcloud.com/test_user",
            "description": "Test bio",
            "followers_count": 1000,
            "country_code": "FR",
            "avatar_url": "https://example.com/avatar.jpg"
        }

        social_links = [
            SocialLink(platform="facebook", url="https://facebook.com/test_user"),
            SocialLink(platform="instagram", url="https://instagram.com/test_user"),
            SocialLink(platform="website", url="https://example.com")
        ]

        profile = SoundcloudMappingUtils.build_profile(user_data, social_links)

        assert isinstance(profile, SoundcloudProfile)
        assert profile.id == 123456
        assert profile.name == "test_user"
        assert str(profile.url) == "https://soundcloud.com/test_user"
        assert profile.bio == "Test bio"
        assert profile.followers_count == 1000
        assert profile.location == "France"
        assert str(profile.avatar_url) == "https://example.com/avatar.jpg"
        assert len(profile.social_links) == 3

    def test_build_profile_url_with_permalink_url(self):
        user_data = {"permalink_url": "https://soundcloud.com/test_user"}

        url = SoundcloudMappingUtils.build_profile_url(user_data)

        assert url == "https://soundcloud.com/test_user"

    def test_build_profile_url_with_permalink(self):
        user_data = {"permalink": "test_user"}

        url = SoundcloudMappingUtils.build_profile_url(user_data)

        assert url == f"{SOUNDCLOUD_BASE_URL}/test_user"

    def test_build_profile_url_with_no_data(self):
        user_data = {}

        url = SoundcloudMappingUtils.build_profile_url(user_data)

        assert url is None

    @patch('app.scrapers.soundcloud.soundcloud_mapping_utils.PYCOUNTRY_AVAILABLE', True)
    @patch('pycountry.countries.get')
    def test_get_country_name_with_alpha2(self, mock_get):
        country_code = "FR"
        mock_country = type('obj', (object,), {'name': 'France'})
        mock_get.return_value = mock_country

        country_name = SoundcloudMappingUtils.get_country_name(country_code)

        assert country_name == "France"
        mock_get.assert_called_once_with(alpha_2="FR")

    @patch('app.scrapers.soundcloud.soundcloud_mapping_utils.PYCOUNTRY_AVAILABLE', True)
    @patch('pycountry.countries.get')
    def test_get_country_name_with_alpha3(self, mock_get):
        country_code = "FRA"
        mock_country = type('obj', (object,), {'name': 'France'})
        mock_get.return_value = mock_country

        country_name = SoundcloudMappingUtils.get_country_name(country_code)

        assert country_name == "France"
        mock_get.assert_called_once_with(alpha_3="FRA")

    @patch('app.scrapers.soundcloud.soundcloud_mapping_utils.PYCOUNTRY_AVAILABLE', True)
    @patch('pycountry.countries.get')
    def test_get_country_name_with_invalid_code(self, mock_get):
        country_code = "XX"
        mock_get.return_value = None

        country_name = SoundcloudMappingUtils.get_country_name(country_code)

        assert country_name == "XX"

    @patch('app.scrapers.soundcloud.soundcloud_mapping_utils.PYCOUNTRY_AVAILABLE', True)
    @patch('pycountry.countries.get')
    def test_get_country_name_with_exception(self, mock_get):
        country_code = "FR"
        mock_get.side_effect = KeyError("Invalid country")

        country_name = SoundcloudMappingUtils.get_country_name(country_code)

        assert country_name == "FR"

    @patch('app.scrapers.soundcloud.soundcloud_mapping_utils.PYCOUNTRY_AVAILABLE', False)
    def test_get_country_name_without_pycountry(self):
        country_code = "FR"

        country_name = SoundcloudMappingUtils.get_country_name(country_code)

        assert country_name == "FR"

    def test_get_country_name_none(self):
        country_name = SoundcloudMappingUtils.get_country_name(None)

        assert country_name is None

    def test_extract_social_links(self, mock_soundcloud_webprofiles_data):
        social_links = SoundcloudMappingUtils.extract_social_links(mock_soundcloud_webprofiles_data)

        assert len(social_links) == 3

        platforms = [link.platform.value for link in social_links]
        assert "facebook" in platforms
        assert "website" in platforms  # "personal" est converti en "website"

        for link in social_links:
            if str(link.url) == "https://example.com/":
                assert link.platform.value == "website"
