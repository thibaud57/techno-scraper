import asyncio
import logging

from app.core.errors import ParsingException, ResourceNotFoundException
from app.models import SoundcloudProfile
from app.scrapers.base_scraper import BaseScraper
from app.scrapers.soundcloud.soundcloud_mapping_utils import SoundcloudMappingUtils
from app.scrapers.soundcloud.soundcloud_webprofiles_scraper import SoundcloudWebprofilesScraper

logger = logging.getLogger(__name__)


class SoundcloudProfileScraper(BaseScraper):

    async def scrape(self, user_id: int) -> SoundcloudProfile:
        logger.info(f"Récupération du profil par ID: {user_id}")

        # Scraping du profil
        profile_url = SoundcloudMappingUtils.build_api_user_url(user_id)
        profile_task = self.fetch(profile_url)

        # Scraping des réseaux sociaux
        webprofiles_scraper = SoundcloudWebprofilesScraper()
        webprofiles_task = webprofiles_scraper.scrape(user_id)

        # Attendre les deux résultats (gestion des erreurs séparément)
        profile_response, social_links = await asyncio.gather(
            profile_task,
            webprofiles_task,
            return_exceptions=True
        )

        if isinstance(profile_response, Exception):
            raise profile_response
        if profile_response.status_code == 404:
            raise ResourceNotFoundException(
                resource_type="Profil Soundcloud",
                resource_id=str(user_id)
            )

        try:
            # Extraire les données JSON du profil
            profile_data = profile_response.json()
            if profile_data.get("kind") != "user":
                raise ParsingException(
                    message=f"Le résultat n'est pas un profil utilisateur pour l'ID: {user_id}",
                    details={"url": profile_url, "kind": profile_data.get("kind")}
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
                    details={"url": profile_url, "error": str(e)}
                )
            raise
