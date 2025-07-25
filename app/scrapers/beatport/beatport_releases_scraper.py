import json
import logging
import re
from datetime import date, datetime
from typing import Dict, Any, Optional
from urllib.parse import urlencode

from app.core.errors import ParsingException, ResourceNotFoundException
from app.models import LimitEnum
from app.models.beatport_models import (
    BeatportEntityType,
    BeatportReleasesResult,
    BeatportFacets,
    BeatportFacetFields,
    BeatportFacetItem
)
from app.scrapers.base_scraper import BaseScraper
from app.scrapers.beatport.beatport_mapping_utils import BeatportMappingUtils

logger = logging.getLogger(__name__)


class BeatportReleasesScraper(BaseScraper):
    """Scraper pour les releases sur Beatport"""

    async def scrape(
            self,
            entity_type: BeatportEntityType,
            entity_slug: str,
            entity_id: str,
            page: int = 1,
            limit: LimitEnum = LimitEnum.TEN,
            start_date: Optional[date] = None,
            end_date: Optional[date] = None
    ) -> BeatportReleasesResult:
        logger.info(f"Récupération des releases pour {entity_type.value}: '{entity_slug}' (ID: {entity_id})")

        # Construire l'URL avec les paramètres
        releases_url = self._build_releases_url(
            entity_type=entity_type,
            entity_slug=entity_slug,
            entity_id=entity_id,
            page=page,
            per_page=limit.value,
            start_date=start_date,
            end_date=end_date
        )

        # Récupérer la page HTML
        response = await self.fetch(releases_url)

        if response.status_code == 404:
            raise ResourceNotFoundException(
                resource_type=f"{entity_type.value.capitalize()} Beatport",
                resource_id=entity_slug,
                details={"id": entity_id}
            )

        try:
            # Extraire les données JSON du script NEXT_DATA
            html_content = response.text
            next_data_json = self._extract_next_data(html_content)

            if not next_data_json:
                raise ParsingException(
                    message=f"Impossible de trouver les données NEXT_DATA pour {entity_type.value} '{entity_slug}'",
                    details={"url": releases_url}
                )

            result = self._extract_releases_and_facets(next_data_json)

            logger.info(
                f"Releases récupérées pour {entity_type.value} '{entity_slug}': {len(result.releases)} trouvées")

            return result

        except Exception as e:
            if not isinstance(e, (ResourceNotFoundException, ParsingException)):
                raise ParsingException(
                    message=f"Erreur lors du parsing des releases pour {entity_type.value} '{entity_slug}': {str(e)}",
                    details={"url": releases_url, "error": str(e)}
                )
            raise

    def _build_releases_url(
            self,
            entity_type: BeatportEntityType,
            entity_slug: str,
            entity_id: str,
            page: int = 1,
            per_page: int = 25,
            start_date: Optional[date] = None,
            end_date: Optional[date] = None
    ) -> str:
        base_url = BeatportMappingUtils.build_url(entity_type, entity_slug, entity_id) + "/releases"

        # Construction de la requête
        query_params = {}

        # Ajouter la pagination
        query_params["page"] = page
        query_params["per_page"] = per_page

        # Ajouter le filtre de dates si spécifié
        if start_date or end_date:
            # Par défaut, la date de fin est aujourd'hui si non spécifiée
            if start_date and not end_date:
                end_date = datetime.now().date()
            # Par défaut, la date de début est un an avant la date de fin si non spécifiée
            if end_date and not start_date:
                start_date = date(end_date.year - 1, end_date.month, end_date.day)

            # Formater les dates au format YYYY-MM-DD
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")

            # Ajouter le paramètre publish_date au format start_date:end_date
            query_params["publish_date"] = f"{start_date_str}:{end_date_str}"

        return f"{base_url}?{urlencode(query_params)}"

    def _extract_next_data(self, html_content: str) -> Dict[str, Any]:
        # Rechercher le script avec l'ID __NEXT_DATA__
        pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
        match = re.search(pattern, html_content, re.DOTALL)

        if not match:
            # Log de debug, l'exception sera levée par l'appelant
            logger.error("Script __NEXT_DATA__ non trouvé dans la page HTML")
            return {}

        # Extraire et parser le JSON
        json_str = match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            # Log de debug, l'exception sera levée par l'appelant
            logger.error(f"Erreur lors du parsing JSON: {str(e)}")
            return {}

    def _extract_releases_and_facets(self, next_data: Dict[str, Any]) -> BeatportReleasesResult:
        # Extraire les releases et les facets des données JSON
        try:
            data = self._find_releases_and_facets_data(next_data)

            if not data:
                logger.warning("Aucune donnée trouvée dans NEXT_DATA")
                return BeatportReleasesResult()

            # Extraire les releases
            releases_data = data.get("results", [])
            extracted_releases = []

            if releases_data:
                for release_data in releases_data:
                    try:
                        release = BeatportMappingUtils.extract_release(release_data)
                        extracted_releases.append(release)
                    except Exception as e:
                        logger.warning(f"Erreur lors de l'extraction d'une release: {str(e)}")

            # Extraire les facets
            facets_data = data.get("facets", {})
            facets = self._extract_facets(facets_data) if facets_data else None

            return BeatportReleasesResult(releases=extracted_releases, facets=facets)

        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des releases et facets: {str(e)}")
            return BeatportReleasesResult()

    def _find_releases_and_facets_data(self, next_data: Dict[str, Any]) -> Dict[str, Any]:
        # Trouver les données de releases et facets dans la structure JSON
        try:
            props = next_data.get("props", {})
            page_props = props.get("pageProps", {})
            dehydrated_state = page_props.get("dehydratedState", {})
            queries = dehydrated_state.get("queries", [])

            # Parcourir les queries pour trouver celle qui contient les releases
            for query in queries:
                query_key = query.get("queryKey", [""])[0]
                if "releases" in str(query_key).lower() and "state" in query and "data" in query["state"]:
                    data = query["state"]["data"]
                    if "results" in data and isinstance(data["results"], list):
                        logger.info(f"Trouvé {len(data['results'])} releases dans results")
                        return data  # Retourne toute la structure data qui contient results et facets

            logger.warning("Aucune structure de données de releases reconnue dans next_data_json")
            return {}
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des données de releases et facets: {str(e)}")
            return {}

    def _extract_facets(self, facets_data: Dict[str, Any]) -> Optional[BeatportFacets]:
        # Extraire les facets des données JSON
        try:
            if not facets_data or "fields" not in facets_data:
                logger.warning("Aucune donnée de facets trouvée")
                return None

            fields_data = facets_data["fields"]
            facet_fields = BeatportFacetFields()

            # Extraire seulement les genres
            if "genre" in fields_data and isinstance(fields_data["genre"], list):
                genre_items = []
                for item_data in fields_data["genre"]:
                    if isinstance(item_data, dict) and all(key in item_data for key in ["name", "count"]):
                        facet_item = BeatportFacetItem(
                            name=item_data["name"],
                            count=item_data["count"]
                        )
                        genre_items.append(facet_item)

                facet_fields.genre = genre_items

            return BeatportFacets(fields=facet_fields)

        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des facets: {str(e)}")
            return None
