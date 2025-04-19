import logging
from typing import Any, Dict
from urllib.parse import quote

from app.core.errors import ParsingException, ResourceNotFoundException
from app.models import SoundcloudSearchResult, LimitEnum
from app.scrapers.base_scraper import BaseScraper
from app.scrapers.soundcloud.soundcloud_mapping_utils import \
    SoundcloudMappingUtils

logger = logging.getLogger(__name__)


class SoundcloudSearchProfileScraper(BaseScraper):

    async def scrape(self, name: str, page: int = 1, limit: LimitEnum = LimitEnum.TEN) -> SoundcloudSearchResult:
        logger.info(f"Recherche de profils pour: '{name}'")
        
        encoded_query = quote(name)
        api_url = SoundcloudMappingUtils.build_api_url_with_pagination(encoded_query, page, limit)
        
        response = await self.fetch(api_url)
        
        if response.status_code == 404:
            raise ResourceNotFoundException(
                resource_type="Recherche de profils Soundcloud",
                resource_id=name
            )

        try:
            json_data = response.json()
            search_result = self._build_search_result_from_api(json_data, page, limit)
            logger.info(f"Recherche terminée: {len(search_result.profiles)} profils trouvés (page {page})")
            return search_result

        except Exception as e:
            if not isinstance(e, (ResourceNotFoundException, ParsingException)):
                raise ParsingException(
                    message=f"Erreur lors du parsing de la recherche pour '{name}': {str(e)}",
                    details={"url": api_url, "error": str(e)}
                )
            raise

    def _build_search_result_from_api(self, json_data: Dict[str, Any], page: int, limit: LimitEnum) -> SoundcloudSearchResult:
        total_results = json_data.get("total_results", 0)
        
        profiles = []
        collection = json_data.get("collection", [])
        
        for user_data in collection:
            if user_data.get("kind") == "user":
                profile = SoundcloudMappingUtils.build_profile(user_data)
                profiles.append(profile)
        

        return SoundcloudSearchResult(
            total_results=total_results,
            page=page,
            limit=limit,
            profiles=profiles
        ) 