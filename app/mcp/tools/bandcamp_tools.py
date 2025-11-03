import json
import logging
from typing import Any

from mcp.types import Tool

from app.models.bandcamp_models import BandcampEntityType
from app.scrapers.bandcamp import BandcampSearchScraper

logger = logging.getLogger(__name__)


bandcamp_search_tool = Tool(
    name="bandcamp_search",
    description="Search for artist and label profiles on Bandcamp by name or keyword. Returns a list of bands (artists/labels) with id, name, url, avatar_url, location, and genre information.",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Artist name, label name, or search keyword"
            },
            "page": {
                "type": "integer",
                "description": "Page number for pagination (default: 1)",
                "default": 1
            },
            "entity_type": {
                "type": "string",
                "description": "Search type: 'bands' for artists/labels or 'tracks' for music tracks (default: 'bands')",
                "enum": ["bands", "tracks"],
                "default": "bands"
            }
        },
        "required": ["query"]
    }
)


async def execute_bandcamp_search(
    query: str,
    page: int = 1,
    entity_type: str = "bands"
) -> dict[str, Any]:
    try:
        entity_type_enum = BandcampEntityType.BANDS
        if entity_type == "tracks":
            entity_type_enum = BandcampEntityType.TRACKS

        scraper = BandcampSearchScraper()
        result = await scraper.scrape(
            query=query,
            page=page,
            entity_type=entity_type_enum
        )

        return json.loads(result.model_dump_json())

    except Exception as e:
        logger.error(f"Error executing bandcamp_search: {e}")
        return {
            "error": str(e),
            "tool": "bandcamp_search",
            "query": query
        }
