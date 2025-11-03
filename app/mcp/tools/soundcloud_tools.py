import json
import logging
from typing import Any

from mcp.types import Tool, TextContent

from app.models import LimitEnum
from app.scrapers.soundcloud import SoundcloudSearchProfileScraper, SoundcloudProfileScraper

logger = logging.getLogger(__name__)


soundcloud_search_profiles_tool = Tool(
    name="soundcloud_search_profiles",
    description="Search for artist profiles on SoundCloud by name or keyword. Returns profile information including bio, location, followers count, and social media links.",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Artist name or search keyword to find profiles"
            },
            "page": {
                "type": "integer",
                "description": "Page number for pagination (default: 1)",
                "default": 1
            },
            "limit": {
                "type": "integer",
                "description": "Number of results per page: 10, 25, or 50 (default: 10)",
                "enum": [10, 25, 50],
                "default": 10
            }
        },
        "required": ["query"]
    }
)


soundcloud_get_profile_tool = Tool(
    name="soundcloud_get_profile",
    description="Get detailed profile information for a specific SoundCloud user by their user ID. Returns profile data including bio, location, followers count, and social media links.",
    inputSchema={
        "type": "object",
        "properties": {
            "user_id": {
                "type": "integer",
                "description": "SoundCloud user ID to retrieve profile information"
            }
        },
        "required": ["user_id"]
    }
)


async def execute_soundcloud_search(query: str, page: int = 1, limit: int = 10) -> dict[str, Any]:
    try:
        limit_enum = LimitEnum.TEN
        if limit == 25:
            limit_enum = LimitEnum.TWENTY_FIVE
        elif limit == 50:
            limit_enum = LimitEnum.FIFTY

        scraper = SoundcloudSearchProfileScraper()
        result = await scraper.scrape(name=query, page=page, limit=limit_enum)

        return json.loads(result.model_dump_json())

    except Exception as e:
        logger.error(f"Error executing soundcloud_search_profiles: {e}")
        return {
            "error": str(e),
            "tool": "soundcloud_search_profiles",
            "query": query
        }


async def execute_soundcloud_get_profile(user_id: int) -> dict[str, Any]:
    try:
        scraper = SoundcloudProfileScraper()
        result = await scraper.scrape(user_id=user_id)

        return json.loads(result.model_dump_json())

    except Exception as e:
        logger.error(f"Error executing soundcloud_get_profile: {e}")
        return {
            "error": str(e),
            "tool": "soundcloud_get_profile",
            "user_id": user_id
        }
