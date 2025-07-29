import asyncio
import logging

from app.core.errors import ParsingException, ResourceNotFoundException
from app.models import SoundcloudProfile
from app.scrapers.base_scraper import BaseScraper
from app.scrapers.soundcloud.soundcloud_mapping_utils import SoundcloudMappingUtils
from app.scrapers.soundcloud.soundcloud_webprofiles_scraper import SoundcloudWebprofilesScraper
from app.services.soundcloud import soundcloud_api

logger = logging.getLogger(__name__)


class SoundcloudProfileScraper(BaseScraper):
    """Scraper pour un profil Soundcloud"""

    async def scrape(self, user_id: int) -> SoundcloudProfile:
        logger.info(f"Récupération du profil par ID: {user_id}")

        # Scraping du profil et des réseaux sociaux en parallèle
        webprofiles_scraper = SoundcloudWebprofilesScraper()
        
        # Exécuter les deux requêtes en parallèle
        profile_data, social_links = await asyncio.gather(
            soundcloud_api.get_user(user_id),
            webprofiles_scraper.scrape(user_id),
            return_exceptions=True
        )

        # Gérer les erreurs du profil
        if isinstance(profile_data, Exception):
            raise profile_data

        try:
            # Vérifier que le résultat est bien un profil utilisateur
            if profile_data.get("kind") != "user":
                raise ParsingException(
                    message=f"Le résultat n'est pas un profil utilisateur pour l'ID: {user_id}",
                    details={"kind": profile_data.get("kind")}
                )

            # Si les réseaux sociaux sont erronés, on passe un tableau vide
            if isinstance(social_links, Exception):
                logger.warning(f"Erreur lors de la récupération des réseaux sociaux: {str(social_links)}")
                social_links = []

            # Construire le profil avec les réseaux sociaux
            profile = SoundcloudMappingUtils.build_profile(profile_data, social_links)

            logger.info(f"Profil récupéré par ID: {profile.name}")
            return profile

        except Exception as e:
            if not isinstance(e, (ResourceNotFoundException, ParsingException)):
                raise ParsingException(
                    message=f"Erreur lors du parsing du profil avec ID {user_id}: {str(e)}",
                    details={"error": str(e)}
                )
            raise
