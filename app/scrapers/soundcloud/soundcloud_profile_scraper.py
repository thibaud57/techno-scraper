import logging
from typing import Any, Dict

from app.core.errors import ParsingException, ResourceNotFoundException
from app.models import SoundcloudProfile
from app.scrapers.base_scraper import BaseScraper
from app.scrapers.soundcloud.soundcloud_mapping_utils import SoundcloudMappingUtils

logger = logging.getLogger(__name__)


class SoundcloudProfileScraper(BaseScraper):

    async def scrape(self, user_id: int) -> SoundcloudProfile:
        logger.info(f"Récupération du profil par ID: {user_id}")
        
        api_url = SoundcloudMappingUtils.build_api_user_url(user_id)
        
        response = await self.fetch(api_url)
        
        if response.status_code == 404:
            raise ResourceNotFoundException(
                resource_type="Profil Soundcloud",
                resource_id=str(user_id)
            )

        try:
            json_data = response.json()
            
            if json_data.get("kind") != "user":
                raise ParsingException(
                    message=f"Le résultat n'est pas un profil utilisateur pour l'ID: {user_id}",
                    details={"url": api_url, "kind": json_data.get("kind")}
                )
            
            profile = SoundcloudMappingUtils.build_profile(json_data)
            
            logger.info(f"Profil récupéré par ID: {profile.name}")
            return profile

        except Exception as e:
            if not isinstance(e, (ResourceNotFoundException, ParsingException)):
                raise ParsingException(
                    message=f"Erreur lors du parsing du profil avec ID {user_id}: {str(e)}",
                    details={"url": api_url, "error": str(e)}
                )
            raise

