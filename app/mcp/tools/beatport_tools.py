import json
import logging
from datetime import date
from typing import Any, Optional

from mcp.types import Tool

from app.models import LimitEnum
from app.models.beatport_models import BeatportEntityType, BeatportReleaseEntityType
from app.scrapers.beatport import BeatportSearchScraper, BeatportReleasesScraper

logger = logging.getLogger(__name__)


beatport_search_tool = Tool(
    name="beatport_search",
    description="Search for artists, labels, tracks, or releases on Beatport by name or keyword. Returns lists of matching entities with id, name, url, and avatar_url. Use entity_type_filter='label' to search only for labels.",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Label name, artist name, or search keyword"
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
            },
            "entity_type": {
                "type": "string",
                "description": "Filter results by entity type: 'artist', 'label', 'track', 'release', or null for all types (default: null)",
                "enum": ["artist", "label", "track", "release"],
                "default": None
            }
        },
        "required": ["query"]
    }
)


beatport_get_label_releases_tool = Tool(
    name="beatport_get_label_releases",
    description="Get releases for a specific Beatport label with genre facets. Returns a list of releases and facets containing genre statistics (name and count). Useful for determining the main genre of a label and analyzing its activity.",
    inputSchema={
        "type": "object",
        "properties": {
            "entity_slug": {
                "type": "string",
                "description": "Label slug (URL-friendly name, e.g., 'drumzone-records')"
            },
            "entity_id": {
                "type": "string",
                "description": "Label ID (numeric identifier as string, e.g., '22038')"
            },
            "page": {
                "type": "integer",
                "description": "Page number for pagination (default: 1)",
                "default": 1
            },
            "limit": {
                "type": "integer",
                "description": "Number of results per page: 10, 25, or 50 (default: 25)",
                "enum": [10, 25, 50],
                "default": 25
            },
            "start_date": {
                "type": "string",
                "description": "Filter releases from this date (format: YYYY-MM-DD). Example: '2024-01-15'",
                "default": None
            }
        },
        "required": ["entity_slug", "entity_id"]
    }
)


async def execute_beatport_search(
    query: str,
    page: int = 1,
    limit: int = 10,
    entity_type: Optional[str] = None
) -> dict[str, Any]:
    try:
        limit_enum = LimitEnum.TEN
        if limit == 25:
            limit_enum = LimitEnum.TWENTY_FIVE
        elif limit == 50:
            limit_enum = LimitEnum.FIFTY

        entity_type_filter = None
        if entity_type:
            entity_type_filter = BeatportEntityType(entity_type)

        scraper = BeatportSearchScraper()
        result = await scraper.scrape(
            query=query,
            page=page,
            limit=limit_enum,
            entity_type_filter=entity_type_filter
        )

        return json.loads(result.model_dump_json())

    except Exception as e:
        logger.error(f"Error executing beatport_search: {e}")
        return {
            "error": str(e),
            "tool": "beatport_search",
            "query": query
        }


async def execute_beatport_get_label_releases(
    entity_slug: str,
    entity_id: str,
    page: int = 1,
    limit: int = 25,
    start_date: Optional[str] = None
) -> dict[str, Any]:
    try:
        limit_enum = LimitEnum.TEN
        if limit == 25:
            limit_enum = LimitEnum.TWENTY_FIVE
        elif limit == 50:
            limit_enum = LimitEnum.FIFTY

        start_date_obj = None
        if start_date:
            try:
                start_date_obj = date.fromisoformat(start_date)
            except ValueError:
                logger.warning(f"Invalid date format: {start_date}, ignoring")

        scraper = BeatportReleasesScraper()
        result = await scraper.scrape(
            entity_type=BeatportEntityType.LABEL,
            entity_slug=entity_slug,
            entity_id=entity_id,
            page=page,
            limit=limit_enum,
            start_date=start_date_obj
        )

        return json.loads(result.model_dump_json())

    except Exception as e:
        logger.error(f"Error executing beatport_get_label_releases: {e}")
        return {
            "error": str(e),
            "tool": "beatport_get_label_releases",
            "entity_slug": entity_slug,
            "entity_id": entity_id
        }
