import pytest
from bs4 import BeautifulSoup

from app.models.bandcamp_models import BandcampEntityType
from app.scrapers.bandcamp.bandcamp_mapping_utils import BandcampMappingUtils


class TestBandcampMappingUtils:

    def test_build_url_bands(self):
        """Test de construction d'URL pour recherche d'artistes/labels"""
        url = BandcampMappingUtils.build_url(BandcampEntityType.BANDS, "test artist")
        assert url == "https://bandcamp.com/search?q=test%20artist&item_type=b"

    def test_build_url_tracks(self):
        """Test de construction d'URL pour recherche de tracks"""
        url = BandcampMappingUtils.build_url(BandcampEntityType.TRACKS, "test track")
        assert url == "https://bandcamp.com/search?q=test%20track&item_type=t"

    def test_build_url_with_special_characters(self):
        """Test de construction d'URL avec caractères spéciaux"""
        url = BandcampMappingUtils.build_url(BandcampEntityType.BANDS, "test & artist!")
        assert url == "https://bandcamp.com/search?q=test%20%26%20artist%21&item_type=b"

    def test_extract_profile_complete(self):
        """Test d'extraction d'un profil complet"""
        html = """
        <li class="searchresult">
            <div class="art">
                <img src="https://f4.bcbits.com/img/a123456789_1.jpg" alt="avatar">
            </div>
            <div class="heading">
                <a href="https://mutual-rytm.bandcamp.com">Mutual Rytm</a>
            </div>
            <div class="subhead">Berlin, Germany</div>
            <div class="genre">electronic</div>
        </li>
        """
        soup = BeautifulSoup(html, 'html.parser')
        result_element = soup.find('li', class_='searchresult')
        
        profile = BandcampMappingUtils.extract_profile(result_element)
        
        assert profile is not None
        assert profile.name == "Mutual Rytm"
        assert "https://mutual-rytm.bandcamp.com" in str(profile.url)
        assert profile.location == "Germany"
        assert profile.genre == "electronic"
        assert str(profile.avatar_url) == "https://f4.bcbits.com/img/a123456789_1.jpg"
        assert profile.id > 0

    def test_extract_profile_minimal(self):
        """Test d'extraction d'un profil avec données minimales"""
        html = """
        <li class="searchresult">
            <div class="heading">
                <a href="https://test-artist.bandcamp.com">Test Artist</a>
            </div>
        </li>
        """
        soup = BeautifulSoup(html, 'html.parser')
        result_element = soup.find('li', class_='searchresult')
        
        profile = BandcampMappingUtils.extract_profile(result_element)
        
        assert profile is not None
        assert profile.name == "Test Artist"
        assert "https://test-artist.bandcamp.com" in str(profile.url)
        assert profile.location is None
        assert profile.genre is None
        assert profile.avatar_url is None
        assert profile.id > 0

    def test_extract_profile_no_heading(self):
        """Test d'extraction sans élément heading"""
        html = """
        <li class="searchresult">
            <div class="art">
                <img src="test.jpg" alt="avatar">
            </div>
        </li>
        """
        soup = BeautifulSoup(html, 'html.parser')
        result_element = soup.find('li', class_='searchresult')
        
        profile = BandcampMappingUtils.extract_profile(result_element)
        
        assert profile is None

    def test_extract_profile_no_link(self):
        """Test d'extraction sans lien dans heading"""
        html = """
        <li class="searchresult">
            <div class="heading">
                <span>Test Artist</span>
            </div>
        </li>
        """
        soup = BeautifulSoup(html, 'html.parser')
        result_element = soup.find('li', class_='searchresult')
        
        profile = BandcampMappingUtils.extract_profile(result_element)
        
        assert profile is None

    def test_extract_avatar_url_present(self):
        """Test d'extraction d'avatar URL présente"""
        html = """
        <div class="art">
            <img src="https://f4.bcbits.com/img/avatar.jpg" alt="avatar">
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        result_element = soup.find('div', class_='art')
        
        avatar_url = BandcampMappingUtils._extract_avatar_url(result_element.parent)
        
        assert avatar_url == "https://f4.bcbits.com/img/avatar.jpg"

    def test_extract_avatar_url_missing(self):
        """Test d'extraction d'avatar URL manquante"""
        html = """
        <div class="other">
            <span>No avatar</span>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        result_element = soup.find('div')
        
        avatar_url = BandcampMappingUtils._extract_avatar_url(result_element)
        
        assert avatar_url is None

    def test_extract_location_with_city(self):
        """Test d'extraction de location avec ville"""
        html = """
        <div class="subhead">Berlin, Germany</div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        result_element = soup.find('div')
        
        location = BandcampMappingUtils._extract_location(result_element.parent)
        
        assert location == "Germany"

    def test_extract_location_country_only(self):
        """Test d'extraction de location pays uniquement"""
        html = """
        <div class="subhead">France</div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        result_element = soup.find('div')
        
        location = BandcampMappingUtils._extract_location(result_element.parent)
        
        assert location == "France"

    def test_extract_location_missing(self):
        """Test d'extraction de location manquante"""
        html = """
        <div class="other">No location</div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        result_element = soup.find('div')
        
        location = BandcampMappingUtils._extract_location(result_element)
        
        assert location is None

    def test_extract_genre_present(self):
        """Test d'extraction de genre présent"""
        html = """
        <div class="genre">electronic</div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        result_element = soup.find('div')
        
        genre = BandcampMappingUtils._extract_genre(result_element.parent)
        
        assert genre == "electronic"

    def test_extract_genre_with_prefix(self):
        """Test d'extraction de genre avec préfixe"""
        html = """
        <div class="genre">genre: techno</div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        result_element = soup.find('div')
        
        genre = BandcampMappingUtils._extract_genre(result_element.parent)
        
        assert genre == "techno"

    def test_extract_genre_missing(self):
        """Test d'extraction de genre manquant"""
        html = """
        <div class="other">No genre</div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        result_element = soup.find('div')
        
        genre = BandcampMappingUtils._extract_genre(result_element)
        
        assert genre is None

    def test_clean_bandcamp_url_simple(self):
        """Test de nettoyage d'URL simple"""
        url = "https://test-artist.bandcamp.com/music"
        cleaned = BandcampMappingUtils._clean_bandcamp_url(url)
        assert cleaned == "https://test-artist.bandcamp.com"

    def test_clean_bandcamp_url_with_params(self):
        """Test de nettoyage d'URL avec paramètres"""
        url = "https://test-artist.bandcamp.com/album/test?param=value"
        cleaned = BandcampMappingUtils._clean_bandcamp_url(url)
        assert cleaned == "https://test-artist.bandcamp.com"

    def test_clean_bandcamp_url_trailing_slash(self):
        """Test de nettoyage d'URL avec slash final"""
        url = "https://test-artist.bandcamp.com/"
        cleaned = BandcampMappingUtils._clean_bandcamp_url(url)
        assert cleaned == "https://test-artist.bandcamp.com"

    def test_clean_bandcamp_url_empty(self):
        """Test de nettoyage d'URL vide"""
        cleaned = BandcampMappingUtils._clean_bandcamp_url("")
        assert cleaned == ""

    def test_clean_bandcamp_url_none(self):
        """Test de nettoyage d'URL None"""
        cleaned = BandcampMappingUtils._clean_bandcamp_url(None)
        assert cleaned is None

    def test_generate_id_from_url_standard(self):
        """Test de génération d'ID depuis URL standard"""
        url = "https://mutual-rytm.bandcamp.com"
        id_value = BandcampMappingUtils._generate_id_from_url(url)
        assert isinstance(id_value, int)
        assert id_value > 0

    def test_generate_id_from_url_consistency(self):
        """Test de cohérence de génération d'ID"""
        url = "https://test-artist.bandcamp.com"
        id1 = BandcampMappingUtils._generate_id_from_url(url)
        id2 = BandcampMappingUtils._generate_id_from_url(url)
        assert id1 == id2

    def test_generate_id_from_url_different_urls(self):
        """Test de génération d'ID différents pour URLs différentes"""
        url1 = "https://artist1.bandcamp.com"
        url2 = "https://artist2.bandcamp.com"
        id1 = BandcampMappingUtils._generate_id_from_url(url1)
        id2 = BandcampMappingUtils._generate_id_from_url(url2)
        assert id1 != id2

    def test_generate_id_from_url_empty(self):
        """Test de génération d'ID depuis URL vide"""
        id_value = BandcampMappingUtils._generate_id_from_url("")
        assert id_value == 0

    def test_generate_id_from_url_none(self):
        """Test de génération d'ID depuis URL None"""
        id_value = BandcampMappingUtils._generate_id_from_url(None)
        assert id_value == 0