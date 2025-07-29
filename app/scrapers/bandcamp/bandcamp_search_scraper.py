import logging
from typing import List

from bs4 import BeautifulSoup

from app.core.errors import ParsingException, ResourceNotFoundException
from app.models import BandcampSearchResult, BandcampBandProfile, BandcampEntityType
from app.scrapers.base_scraper import BaseScraper
from app.scrapers.bandcamp.bandcamp_mapping_utils import BandcampMappingUtils

logger = logging.getLogger(__name__)


class BandcampSearchScraper(BaseScraper):
    """Scraper pour la recherche d'artistes et labels sur Bandcamp"""

    async def scrape(self, query: str, page: int = 1,
                     entity_type: BandcampEntityType = BandcampEntityType.BANDS) -> BandcampSearchResult:
        logger.info(f"Recherche Bandcamp pour: '{query}'")

        # Construire l'URL de recherche
        search_url = BandcampMappingUtils.build_url(entity_type, query)
        params = {'page': page} if page > 1 else {}

        # Récupérer la page HTML
        response = await self.fetch(search_url, params=params)

        if response.status_code == 404:
            raise ResourceNotFoundException(
                resource_type="Recherche Bandcamp",
                resource_id=query
            )

        try:
            # Parser le HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            profiles = self._parse_search_results(soup)

            search_result = BandcampSearchResult(
                bands=profiles
            )

            logger.info(f"Recherche terminée: {len(profiles)} profils trouvés (page {page})")
            return search_result

        except Exception as e:
            if not isinstance(e, (ResourceNotFoundException, ParsingException)):
                raise ParsingException(
                    message=f"Erreur lors du parsing de la recherche Bandcamp pour '{query}': {str(e)}",
                    details={"url": search_url, "error": str(e)}
                )
            raise

    def _parse_search_results(self, soup: BeautifulSoup) -> List[BandcampBandProfile]:
        """Parse les résultats de recherche depuis le HTML"""
        profiles = []

        # Rechercher les résultats d'artistes
        search_results = soup.find_all('li', class_='searchresult')

        for result in search_results:
            profile = BandcampMappingUtils.extract_profile(result)
            if profile:
                profiles.append(profile)

        return profiles
