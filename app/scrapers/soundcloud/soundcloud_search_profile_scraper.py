import asyncio
import logging
from urllib.parse import quote

from app.core.errors import ParsingException, ResourceNotFoundException
from app.models import SoundcloudSearchResult, LimitEnum
from app.scrapers.base_scraper import BaseScraper
from app.scrapers.soundcloud.soundcloud_mapping_utils import SoundcloudMappingUtils
from app.scrapers.soundcloud.soundcloud_webprofiles_scraper import SoundcloudWebprofilesScraper

logger = logging.getLogger(__name__)


class SoundcloudSearchProfileScraper(BaseScraper):
    """Scraper pour la recherche sur Soundcloud"""

    async def scrape(self, name: str, page: int = 1, limit: LimitEnum = LimitEnum.TEN) -> SoundcloudSearchResult:
        logger.info(f"Recherche de profils pour: '{name}'")
        
        # Scraping de la recherche des profils
        encoded_query = quote(name)
        api_url = SoundcloudMappingUtils.build_api_url_with_pagination(encoded_query, page, limit)
        response = await self.fetch(api_url)
        
        if response.status_code == 404:
            raise ResourceNotFoundException(
                resource_type="Recherche de profils Soundcloud",
                resource_id=name
            )

        try:
            # Extraire les données de recherche
            json_data = response.json()
            total_results = json_data.get("total_results", 0)
            collection = json_data.get("collection", [])
            
            # Extraire les profils et leurs réseaux sociaux
            profiles = await self._extract_profiles_with_social_networks(collection)
            
            # Construire et retourner le résultat
            search_result = SoundcloudSearchResult(
                total_results=total_results,
                page=page,
                limit=limit,
                profiles=profiles
            )
            
            logger.info(f"Recherche terminée: {len(profiles)} profils trouvés (page {page})")
            return search_result

        except Exception as e:
            if not isinstance(e, (ResourceNotFoundException, ParsingException)):
                raise ParsingException(
                    message=f"Erreur lors du parsing de la recherche pour '{name}': {str(e)}",
                    details={"url": api_url, "error": str(e)}
                )
            raise

    async def _extract_profiles_with_social_networks(self, collection):
        # Préparation des données de profil et tâches pour les réseaux sociaux
        profile_data_list = []
        webprofile_tasks = []
        webprofiles_scraper = SoundcloudWebprofilesScraper()
        
        # Filtrer et collecter les profils utilisateurs
        for user_data in collection:
            if user_data.get("kind") == "user":
                profile_id = user_data.get("id", 0)
                profile_data_list.append(user_data)
                webprofile_tasks.append(webprofiles_scraper.scrape(profile_id))
        
        # Récupérer tous les réseaux sociaux en parallèle
        social_links_results = []
        if webprofile_tasks:
            social_links_results = await asyncio.gather(*webprofile_tasks, return_exceptions=True)
        
        # Créer les profils en intégrant les réseaux sociaux directement
        profiles = []
        for i, profile_data in enumerate(profile_data_list):
            # Déterminer les réseaux sociaux pour ce profil
            social_links = []
            if i < len(social_links_results):
                if not isinstance(social_links_results[i], Exception):
                    social_links = social_links_results[i]
                else:
                    logger.warning(f"Erreur lors de la récupération des réseaux sociaux pour le profil {profile_data.get('id')}: {str(social_links_results[i])}")
            
            # Construire le profil avec ses réseaux sociaux
            profile = SoundcloudMappingUtils.build_profile(profile_data, social_links)
            profiles.append(profile)
            
        return profiles