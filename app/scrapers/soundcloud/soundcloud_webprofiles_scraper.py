import logging
from typing import List

from app.core.errors import ParsingException, ResourceNotFoundException
from app.models import SocialLink
from app.scrapers.base_scraper import BaseScraper
from app.scrapers.soundcloud.soundcloud_mapping_utils import SoundcloudMappingUtils
from app.services.soundcloud import soundcloud_api

logger = logging.getLogger(__name__)


class SoundcloudWebprofilesScraper(BaseScraper):
    """Scraper pour un les réseaux sociaux Soundcloud"""

    async def scrape(self, user_id: int) -> List[SocialLink]:
        logger.info(f"Récupération des réseaux sociaux pour l'utilisateur ID: {user_id}")

        try:
            # Utiliser le service API pour récupérer les webprofiles
            json_data = await soundcloud_api.get_user_webprofiles(user_id)

            # Mapper les réseaux sociaux
            social_links = SoundcloudMappingUtils.extract_social_links(json_data)

            logger.info(f"Réseaux sociaux récupérés pour l'utilisateur ID {user_id}: {len(social_links)} trouvés")
            return social_links

        except Exception as e:
            if not isinstance(e, (ResourceNotFoundException, ParsingException)):
                raise ParsingException(
                    message=f"Erreur lors du parsing des réseaux sociaux pour l'ID {user_id}: {str(e)}",
                    details={"error": str(e)}
                )
            raise
