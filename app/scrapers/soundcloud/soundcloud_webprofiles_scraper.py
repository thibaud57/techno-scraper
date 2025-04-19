import logging
from typing import Any, Dict, List

from app.core.errors import ParsingException, ResourceNotFoundException
from app.models import SocialLink
from app.scrapers.base_scraper import BaseScraper
from app.scrapers.soundcloud.soundcloud_mapping_utils import SoundcloudMappingUtils

logger = logging.getLogger(__name__)


class SoundcloudWebprofilesScraper(BaseScraper):
    
    async def scrape(self, user_id: int) -> List[SocialLink]:
        logger.info(f"Récupération des réseaux sociaux pour l'utilisateur ID: {user_id}")
        
        api_url = SoundcloudMappingUtils.build_api_webprofiles_url(user_id)
        
        response = await self.fetch(api_url)
        
        if response.status_code == 404:
            raise ResourceNotFoundException(
                resource_type="Webprofiles SoundCloud",
                resource_id=str(user_id)
            )

        try:
            json_data = response.json()
            social_links = SoundcloudMappingUtils.extract_social_links(json_data)
            
            logger.info(f"Réseaux sociaux récupérés pour l'utilisateur ID {user_id}: {len(social_links)} trouvés")
            return social_links

        except Exception as e:
            if not isinstance(e, (ResourceNotFoundException, ParsingException)):
                raise ParsingException(
                    message=f"Erreur lors du parsing des réseaux sociaux pour l'ID {user_id}: {str(e)}",
                    details={"url": api_url, "error": str(e)}
                )
            raise