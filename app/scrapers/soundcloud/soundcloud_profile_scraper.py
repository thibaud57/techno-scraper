import json
import logging
import re
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from app.core.errors import ParsingException, ResourceNotFoundException
from app.models import SoundcloudProfile, Track
from app.scrapers.base_scraper import BaseScraper
from app.scrapers.soundcloud.soundcloud_mapping_utils import SoundcloudMappingUtils

logger = logging.getLogger(__name__)


class SoundcloudProfileScraper(BaseScraper):
    BASE_URL = SoundcloudMappingUtils.BASE_URL

    async def scrape(self, username: str) -> SoundcloudProfile:
        logger.info(f"Récupération du profil: {username}")

        profile_url = f"{self.BASE_URL}/{username}"

        response = await self.fetch(profile_url)

        if response.status_code == 404:
            raise ResourceNotFoundException(
                resource_type="Profil Soundcloud",
                resource_id=username
            )

        soup = BeautifulSoup(response.text, "lxml")

        try:
            json_data = self._extract_json_data(soup)

            if not json_data:
                raise ParsingException(
                    message=f"Impossible d'extraire les données JSON du profil {username}",
                    details={"url": profile_url}
                )

            profile = SoundcloudMappingUtils.build_profile(json_data, profile_url, username)

            logger.info(f"Profil récupéré: {profile.name}")
            return profile

        except Exception as e:
            if not isinstance(e, (ResourceNotFoundException, ParsingException)):
                raise ParsingException(
                    message=f"Erreur lors du parsing du profil {username}: {str(e)}",
                    details={"url": profile_url, "error": str(e)}
                )
            raise

    def _extract_json_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        scripts = soup.find_all("script")

        for script in scripts:
            script_content = script.string
            if script_content and "window.__sc_hydration" in script_content:
                match = re.search(r"window\.__sc_hydration\s*=\s*(\[.*?\]);", script_content, re.DOTALL)
                if match:
                    try:
                        hydration_data = json.loads(match.group(1))

                        for item in hydration_data:
                            if item.get("hydratable") == "user":
                                return item.get("data", {})
                    except json.JSONDecodeError:
                        logger.error("Erreur lors du décodage JSON")

        return {}

