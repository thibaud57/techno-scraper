import json
import logging
import re
from typing import Dict, Any, List

from app.core.errors import ParsingException, ResourceNotFoundException
from app.models import Release, LimitEnum
from app.models.beatport_models import BeatportEntityType
from app.scrapers.base_scraper import BaseScraper
from app.scrapers.beatport.beatport_mapping_utils import BeatportMappingUtils
from app.services.pagination_service import PaginationService

logger = logging.getLogger(__name__)


class BeatportReleasesScraper(BaseScraper):
    """Scraper pour les releases sur Beatport"""

    async def scrape(self, artist_slug: str, page: int = 1, limit: LimitEnum = LimitEnum.TEN) -> List[Release]:
        logger.info(f"Récupération des releases pour l'artiste: '{artist_slug}'")
        
        # Construire l'URL de l'artiste
        artist_url = BeatportMappingUtils.build_url(BeatportEntityType.ARTIST, artist_slug)
        
        # Récupérer la page HTML
        response = await self.fetch(artist_url)
        
        if response.status_code == 404:
            raise ResourceNotFoundException(
                resource_type="Artiste Beatport",
                resource_id=artist_slug
            )
        
        try:
            # Extraire les données JSON du script NEXT_DATA
            html_content = response.text
            next_data_json = self._extract_next_data(html_content)
            
            if not next_data_json:
                raise ParsingException(
                    message=f"Impossible de trouver les données NEXT_DATA pour l'artiste '{artist_slug}'",
                    details={"url": artist_url}
                )
            
            # Extraire les releases
            releases = self._extract_releases(next_data_json, page, limit)
            
            logger.info(f"Releases récupérées pour l'artiste '{artist_slug}': {len(releases)} trouvées")
            
            return releases
            
        except Exception as e:
            if not isinstance(e, (ResourceNotFoundException, ParsingException)):
                raise ParsingException(
                    message=f"Erreur lors du parsing des releases pour l'artiste '{artist_slug}': {str(e)}",
                    details={"url": artist_url, "error": str(e)}
                )
            raise
    
    def _extract_next_data(self, html_content: str) -> Dict[str, Any]:
        # Rechercher le script avec l'ID __NEXT_DATA__
        pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
        match = re.search(pattern, html_content, re.DOTALL)
        
        if not match:
            logger.error("Script __NEXT_DATA__ non trouvé dans la page HTML")
            return {}
        
        # Extraire et parser le JSON
        json_str = match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Erreur lors du parsing JSON: {str(e)}")
            return {}
    
    def _find_releases_data(self, next_data: Dict[str, Any]) -> List:
        # Trouver les données de releases dans la structure JSON
        props = next_data.get("props", {})
        page_props = props.get("pageProps", {})
        dehydrated_state = page_props.get("dehydratedState", {})
        queries = dehydrated_state.get("queries", [])
        
        # Chercher les données de releases dans les queries
        for query in queries:
            if "state" in query and "data" in query["state"]:
                data = query["state"]["data"]
                if isinstance(data, dict) and "releases" in data:
                    return data["releases"]
        
        return []
    
    def _extract_releases(self, next_data: Dict[str, Any], page: int, limit: LimitEnum) -> List[Release]:
        # Extrait les releases des données JSON
        try:
            # Trouver les données de releases
            releases_data = self._find_releases_data(next_data)
            if not releases_data:
                logger.warning("Aucune donnée de releases trouvée dans NEXT_DATA")
                return []
            
            # Extraire chaque release dans une nouvelle liste
            extracted_releases = []
            for release_data in releases_data:
                try:
                    release = BeatportMappingUtils.extract_release(release_data)
                    extracted_releases.append(release)
                except Exception as e:
                    logger.warning(f"Erreur lors de l'extraction d'une release: {str(e)}")
            
            # Appliquer la pagination et retourner une nouvelle liste
            return PaginationService.paginate_results(extracted_releases, page, limit)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des releases: {str(e)}")
            return []