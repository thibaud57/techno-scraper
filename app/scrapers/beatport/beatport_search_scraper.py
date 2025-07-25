import json
import logging
import re
from typing import Dict, Any, List

from app.core.errors import ParsingException, ResourceNotFoundException
from app.models import BeatportSearchResult, LimitEnum
from app.models.beatport_models import BeatportEntityType
from app.scrapers.base_scraper import BaseScraper
from app.scrapers.beatport.beatport_mapping_utils import BeatportMappingUtils
from app.services import PaginationService

logger = logging.getLogger(__name__)


class BeatportSearchScraper(BaseScraper):
    """Scraper pour la recherche sur Beatport"""

    async def scrape(self, query: str, page: int = 1, limit: LimitEnum = LimitEnum.TEN,
                     entity_type_filter: BeatportEntityType = None) -> BeatportSearchResult:
        logger.info(f"Recherche Beatport pour: '{query}'")

        # Construire l'URL de recherche
        search_url = BeatportMappingUtils.build_url(BeatportEntityType.SEARCH, query)

        # Récupérer la page HTML
        response = await self.fetch(search_url)

        if response.status_code == 404:
            raise ResourceNotFoundException(
                resource_type="Recherche Beatport",
                resource_id=query
            )

        try:
            # Extraire les données JSON du script NEXT_DATA
            html_content = response.text
            next_data_json = self._extract_next_data(html_content)

            if not next_data_json:
                raise ParsingException(
                    message=f"Impossible de trouver les données NEXT_DATA pour la recherche '{query}'",
                    details={"url": search_url}
                )

            # Extraire les résultats de recherche
            search_results = self._extract_search_results(next_data_json, page, limit, entity_type_filter)

            logger.info("Recherche Beatport terminée")

            return search_results

        except Exception as e:
            if not isinstance(e, (ResourceNotFoundException, ParsingException)):
                raise ParsingException(
                    message=f"Erreur lors du parsing de la recherche Beatport pour '{query}': {str(e)}",
                    details={"url": search_url, "error": str(e)}
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

    def _extract_search_results(self, next_data: Dict[str, Any], page: int, limit: LimitEnum,
                                entity_type_filter: BeatportEntityType = None) -> BeatportSearchResult:
        # Extrait les résultats de recherche des données JSON
        try:
            # Trouver les données de recherche
            search_data = self._find_search_data(next_data)
            if not search_data:
                logger.warning("Aucune donnée de recherche trouvée dans NEXT_DATA")
                return BeatportSearchResult(
                    total_results=0, page=page, limit=limit,
                    artists=[], tracks=[], releases=[], labels=[]
                )

            # Définir les mappings entre types d'entités et leurs fonctions d'extraction
            entity_mappings = {
                BeatportEntityType.ARTIST: BeatportMappingUtils.extract_artist,
                BeatportEntityType.TRACK: BeatportMappingUtils.extract_track,
                BeatportEntityType.RELEASE: BeatportMappingUtils.extract_release,
                BeatportEntityType.LABEL: BeatportMappingUtils.extract_label
            }

            # Déterminer les entités à traiter
            entities_to_process = list(entity_mappings.keys())
            if entity_type_filter and entity_type_filter != BeatportEntityType.SEARCH:
                entities_to_process = [entity_type_filter]

            # Extraire les résultats pour chaque type d'entité
            artists = []
            tracks = []
            releases = []
            labels = []

            for entity_type in entities_to_process:
                if entity_type in entity_mappings:
                    extract_func = entity_mappings[entity_type]
                    # Assigner les résultats au bon champ avec match case (Python 3.10+)
                    match entity_type:
                        case BeatportEntityType.ARTIST:
                            artists = self._extract_entity_items(search_data, entity_type, extract_func, page, limit)
                        case BeatportEntityType.TRACK:
                            tracks = self._extract_entity_items(search_data, entity_type, extract_func, page, limit)
                        case BeatportEntityType.RELEASE:
                            releases = self._extract_entity_items(search_data, entity_type, extract_func, page, limit)
                        case BeatportEntityType.LABEL:
                            labels = self._extract_entity_items(search_data, entity_type, extract_func, page, limit)

            # Calculer le nombre total de résultats (somme des éléments dans toutes les listes)
            total_results = len(artists) + len(tracks) + len(releases) + len(labels)

            # Construire et retourner le résultat final
            return BeatportSearchResult(
                total_results=total_results,
                page=page,
                limit=limit,
                artists=artists,
                tracks=tracks,
                releases=releases,
                labels=labels
            )

        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des résultats de recherche: {str(e)}")
            return BeatportSearchResult(
                total_results=0, page=page, limit=limit,
                artists=[], tracks=[], releases=[], labels=[]
            )

    def _find_search_data(self, next_data: Dict[str, Any]) -> Dict[str, Any]:
        # Trouve les données de recherche dans la structure JSON"""
        props = next_data.get("props", {})
        page_props = props.get("pageProps", {})
        dehydrated_state = page_props.get("dehydratedState", {})
        queries = dehydrated_state.get("queries", [])

        # Chercher les données de recherche dans les queries
        entity_types = [f"{entity_type.value}s" for entity_type in BeatportEntityType]

        for query in queries:
            if "state" in query and "data" in query["state"]:
                data = query["state"]["data"]
                # Vérifier si les données contiennent au moins une des clés d'entité
                if isinstance(data, dict) and any(entity in data for entity in entity_types):
                    return data

        return {}

    def _extract_entity_items(self, search_data: Dict[str, Any], entity_type: BeatportEntityType,
                              extract_func, page: int, limit: LimitEnum) -> List:
        # Extrait les éléments d'un type d'entité spécifique et retourne une nouvelle liste
        data_field = f"{entity_type.value}s"

        # Vérifier si les données existent
        if data_field not in search_data or "data" not in search_data[data_field]:
            return []

        items_data = search_data[data_field]["data"]
        if not items_data:
            return []

        # Extraire les éléments dans une nouvelle liste
        extracted_items = []
        for item_data in items_data:
            try:
                item = extract_func(item_data)
                extracted_items.append(item)
            except Exception as e:
                logger.warning(f"Erreur lors de l'extraction d'un {entity_type.value}: {str(e)}")

        # Appliquer la pagination et retourner une nouvelle liste
        return PaginationService.paginate_results(extracted_items, page, limit)
