import logging
from typing import Any, Dict, List, Optional

try:
    import pycountry

    PYCOUNTRY_AVAILABLE = True
except ImportError:
    PYCOUNTRY_AVAILABLE = False

from app.models import SocialLink, SoundcloudProfile

logger = logging.getLogger(__name__)

# Constantes pour l'API SoundCloud
SOUNDCLOUD_BASE_URL = "https://soundcloud.com"

class SoundcloudMappingUtils:
    """Utilitaires pour mapper les données SoundCloud vers nos modèles"""

    @staticmethod
    def build_profile(
            user_data: Dict[str, Any],
            social_links: List[SocialLink]
    ) -> SoundcloudProfile:
        profile_url = SoundcloudMappingUtils.build_profile_url(user_data)

        # Utiliser le champ country s'il existe, sinon utiliser country_code
        country_code = user_data.get("country_code") or user_data.get("country")
        country = SoundcloudMappingUtils.get_country_name(country_code)

        return SoundcloudProfile(
            id=user_data.get("id", 0),
            name=user_data.get("username", ""),
            url=profile_url,
            bio=user_data.get("description", ""),
            followers_count=user_data.get("followers_count", 0),
            location=country,
            social_links=social_links,
            avatar_url=user_data.get("avatar_url", None),
        )

    @staticmethod
    def build_profile_url(user_data):
        if "permalink_url" in user_data:
            return user_data.get("permalink_url", "")
        elif "permalink" in user_data:
            permalink = user_data.get("permalink", "")
            if permalink:
                return f"{SOUNDCLOUD_BASE_URL}/{permalink}"
        return None

    @staticmethod
    def get_country_name(country_code: Optional[str]) -> Optional[str]:
        if not country_code:
            return None
        if not PYCOUNTRY_AVAILABLE:
            logger.warning("La bibliothèque pycountry n'est pas disponible. Le code pays ne sera pas converti.")
            return country_code

        try:
            code = country_code.upper()
            country = None
            if len(code) == 2:
                country = pycountry.countries.get(alpha_2=code)
            elif len(code) == 3:
                country = pycountry.countries.get(alpha_3=code)
            if country:
                return country.name
            return country_code
        except (AttributeError, KeyError):
            logger.warning(f"Code pays inconnu: {country_code}")
            return country_code

    @staticmethod
    def extract_social_links(user_data: Dict[str, Any]) -> List[SocialLink]:
        social_links = []

        for item in user_data:
            if "url" in item and ("network" in item or "service" in item):
                network = item.get("service", item.get("network", ""))
                url = item.get("url", "")

                # Convertir 'personal' en 'website'
                if network == "personal":
                    network = "website"

                social_link = SocialLink.from_service(network, url)
                if social_link:
                    social_links.append(social_link)
                else:
                    logger.debug(f"Réseau social non reconnu: {network}")
        return social_links
