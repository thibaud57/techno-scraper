import logging
from typing import Any, Dict, List, Optional

try:
    import pycountry
    PYCOUNTRY_AVAILABLE = True
except ImportError:
    PYCOUNTRY_AVAILABLE = False

from app.models import SocialLink, SoundcloudProfile, Track, LimitEnum

logger = logging.getLogger(__name__)


class SoundcloudMappingUtils:
    BASE_URL = "https://soundcloud.com"
    API_URL = "https://api-v2.soundcloud.com/search/users"
    CLIENT_ID = "EjkRJG0BLNEZquRiPZYdNtJdyGtTuHdp"
    APP_VERSION = "1744919743"
    USER_ID = "50521-276103-240042-666142"

    @staticmethod
    def build_api_url_with_pagination(encoded_query: str, page: int, limit: LimitEnum) -> str: 
        offset = (page - 1) * limit.value
        return f"{SoundcloudMappingUtils.API_URL}?q={encoded_query}&client_id={SoundcloudMappingUtils.CLIENT_ID}&app_version={SoundcloudMappingUtils.APP_VERSION}&user_id={SoundcloudMappingUtils.USER_ID}&limit={limit.value}&offset={offset}"

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
    def build_profile(
            user_data: Dict[str, Any],
            url: Optional[str] = None,
            username: Optional[str] = None
    ) -> SoundcloudProfile:
        profile_url = SoundcloudMappingUtils.build_profile_url(url, user_data)
        username = SoundcloudMappingUtils.build_username(user_data, username)
        social_links = SoundcloudMappingUtils.extract_social_links(user_data)
        country = SoundcloudMappingUtils.get_country_name(user_data.get("country_code"))
        print(user_data)

        return SoundcloudProfile(
            id=user_data.get("id", 0),
            name=user_data.get("username", ""),
            url=profile_url,
            username=username,
            bio=user_data.get("description", ""),
            followers_count=user_data.get("followers_count", 0),
            location=country,
            website=user_data.get("website", None),
            social_links=social_links,
            avatar_url=user_data.get("avatar_url", None),
        )

    @staticmethod
    def build_username(user_data, username):
        user_name = username
        if not user_name:
            user_name = user_data.get("permalink", "")
        return user_name

    @staticmethod
    def build_profile_url(url, user_data):
        profile_url = url
        if not profile_url and "permalink_url" in user_data:
            profile_url = user_data["permalink_url"]
        elif not profile_url and "permalink" in user_data:
            permalink = user_data.get("permalink", "")
            if permalink:
                profile_url = f"{SoundcloudMappingUtils.BASE_URL}/{permalink}"
        return profile_url

    @staticmethod
    def extract_social_links(user_data: Dict[str, Any]) -> List[SocialLink]:
        social_links = []

        # sur le profil du ser y a un script web-profiles avec dedans tout
        # Le permalink il sert à rien là avec le lien soundcloud vu que je l'ai déjà

        # Lien SoundCloud
        if "permalink_url" in user_data:
            social_links.append(SocialLink(
                platform="soundcloud",
                url=user_data["permalink_url"],
            ))
        # Cas où seul le permalink est disponible
        elif "permalink" in user_data:
            permalink = user_data.get("permalink", "")
            if permalink:
                url = f"{SoundcloudMappingUtils.BASE_URL}/{permalink}"
                social_links.append(SocialLink(
                    platform="soundcloud",
                    url=url,
                ))

        # Autres liens sociaux (pas toujours disponibles dans l'API de recherche)
        for network in ["facebook", "instagram"]:
            if f"{network}_url" in user_data and user_data[f"{network}_url"]:
                social_links.append(SocialLink(
                    platform=network,
                    url=user_data[f"{network}_url"],
                ))

        return social_links

    @staticmethod
    def extract_tracks(user_data: Dict[str, Any]) -> Optional[List[Track]]:
        # Cette méthode est un placeholder
        # Dans une implémentation réelle, il faudrait faire une requête supplémentaire
        # pour récupérer les tracks de l'utilisateur
        return None
