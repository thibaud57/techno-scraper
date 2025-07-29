import logging
import re
from typing import Optional
from urllib.parse import urljoin, urlparse, quote

from bs4 import Tag

from app.models import BandcampBandProfile
from app.models.bandcamp_models import BandcampEntityType

logger = logging.getLogger(__name__)

# Constantes pour Bandcamp
BANDCAMP_BASE_URL = "https://bandcamp.com"


class BandcampMappingUtils:
    """Utilitaires pour mapper les données Bandcamp vers nos modèles"""

    @staticmethod
    def build_url(entity_type: BandcampEntityType, query: str) -> str:
        """Construit une URL Bandcamp selon le type d'entité"""
        encoded_query = quote(query)
        return f"{BANDCAMP_BASE_URL}/search?q={encoded_query}&item_type={entity_type.value}"

    @staticmethod
    def extract_profile(result_element: Tag) -> Optional[BandcampBandProfile]:
        """Extrait un profil Bandcamp depuis un élément HTML de résultat de recherche"""
        try:
            # Extraire le nom et l'URL
            name_link = result_element.find('div', class_='heading')
            if not name_link:
                return None

            link_element = name_link.find('a')
            if not link_element:
                return None

            name = link_element.get_text(strip=True)
            url = link_element.get('href')

            # S'assurer que l'URL est absolue
            if url and not url.startswith('http'):
                url = urljoin(BANDCAMP_BASE_URL, url)
            # Nettoyer l'URL
            url = BandcampMappingUtils._clean_bandcamp_url(url)

            # Extraire les champs
            avatar_url = BandcampMappingUtils._extract_avatar_url(result_element)
            location = BandcampMappingUtils._extract_location(result_element)
            genre = BandcampMappingUtils._extract_genre(result_element)
            profile_id = BandcampMappingUtils._generate_id_from_url(url)

            return BandcampBandProfile(
                id=profile_id,
                name=name,
                url=url,
                avatar_url=avatar_url,
                location=location,
                genre=genre
            )

        except Exception as e:
            logger.error(f"Erreur lors de l'extraction d'un profil Bandcamp: {str(e)}")
            return None

    @staticmethod
    def _extract_avatar_url(result_element: Tag) -> Optional[str]:
        """Extrait l'URL de l'avatar depuis l'élément de résultat"""
        try:
            art_div = result_element.find('div', class_='art')
            if not art_div:
                return None

            avatar_img = art_div.find('img')
            return avatar_img.get('src') if avatar_img else None

        except Exception as e:
            logger.error(f"Erreur lors de l'extraction de l'avatar: {str(e)}")
            return None

    @staticmethod
    def _extract_location(result_element: Tag) -> Optional[str]:
        """Extrait le pays depuis l'élément de résultat"""
        try:
            location_elem = result_element.find('div', class_='subhead')
            if not location_elem:
                return None

            full_location = location_elem.get_text(strip=True)
            if not full_location:
                return None

            # Extraire seulement le pays (dernière partie après la virgule)
            if ',' in full_location:
                return full_location.split(',')[-1].strip()
            return full_location

        except Exception as e:
            logger.error(f"Erreur lors de l'extraction de la localisation: {str(e)}")
            return None

    @staticmethod
    def _extract_genre(result_element: Tag) -> Optional[str]:
        """Extrait le genre depuis l'élément de résultat"""
        try:
            genre_elem = result_element.find('div', class_='genre')
            if not genre_elem:
                return None

            genre_text = genre_elem.get_text(strip=True)
            if not genre_text:
                return None

            # Nettoyer le texte du genre (retirer "genre: " si présent)
            if genre_text.lower().startswith('genre:'):
                return genre_text[6:].strip()
            return genre_text

        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du genre: {str(e)}")
            return None

    @staticmethod
    def _clean_bandcamp_url(url: str) -> str:
        """Nettoie l'URL Bandcamp avec regex pour garder seulement le domaine"""
        if not url:
            return url
        # Regex pour extraire https://nom.bandcamp.com (sans slash final ni paramètres)
        match = re.match(r'(https?://[^/?]+)', url)

        if match:
            cleaned = match.group(1).rstrip('/')
            return cleaned
        return url.rstrip('/')

    @staticmethod
    def _generate_id_from_url(url: str) -> int:
        """Génère un ID numérique à partir de l'URL Bandcamp"""
        if not url:
            return 0

        try:
            # Extraire le nom de domaine sans les sous-domaines
            parsed = urlparse(url)
            domain_parts = parsed.netloc.split('.')

            # Prendre la partie principale du domaine (ex: "nom" de "nom.bandcamp.com")
            main_part = domain_parts[0] if len(domain_parts) > 1 else parsed.netloc

            # Convertir en hash numérique positif
            return hash(main_part) & 0x7FFFFFFF

        except Exception as e:
            logger.error(f"Erreur lors de la génération de l'ID: {str(e)}")
            return 0
