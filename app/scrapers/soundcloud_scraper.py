import json
import logging
import re
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from app.core.errors import ParsingException, ResourceNotFoundException
from app.models import SocialLink, SoundcloudProfile, Track
from app.scrapers.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class SoundcloudScraper(BaseScraper):
    BASE_URL = "https://soundcloud.com"

    async def scrape(self, username: str) -> SoundcloudProfile:
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

            profile = self._build_profile(json_data, username, profile_url)

            tracks = self._extract_tracks(json_data)
            if tracks:
                profile.tracks = tracks

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

    def _build_profile(self, json_data: Dict[str, Any], username: str, profile_url: str) -> SoundcloudProfile:
        social_links = self._extract_social_links(json_data)

        return SoundcloudProfile(
            name=json_data.get("username", username),
            url=profile_url,
            bio=json_data.get("description", ""),
            followers_count=json_data.get("followers_count", 0),
            location=json_data.get("city", ""),
            website=json_data.get("website", None),
            social_links=social_links,
            avatar_url=json_data.get("avatar_url", None),
            track_count=json_data.get("track_count", 0),
            reposts_count=json_data.get("reposts_count", 0),
            likes_count=json_data.get("likes_count", 0)
        )

    def _extract_social_links(self, json_data: Dict[str, Any]) -> List[SocialLink]:
        social_links = []

        if "permalink_url" in json_data:
            social_links.append(SocialLink(
                platform="soundcloud",
                url=json_data["permalink_url"],
            ))

        for network in ["facebook", "instagram"]:
            if f"{network}_url" in json_data and json_data[f"{network}_url"]:
                social_links.append(SocialLink(
                    platform=network,
                    url=json_data[f"{network}_url"],
                ))

        return social_links

    def _extract_tracks(self, json_data: Dict[str, Any]) -> Optional[List[Track]]:
        # Cette méthode est un placeholder
        # Dans une implémentation réelle, il faudrait faire une requête supplémentaire
        # pour récupérer les tracks de l'utilisateur
        return None