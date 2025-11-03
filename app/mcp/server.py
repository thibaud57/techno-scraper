import json
import logging
import os
from typing import Any

from mcp.server import Server
from mcp.server.sse import sse_server
from mcp.types import TextContent
from starlette.applications import Starlette
from starlette.routing import Route

from app.mcp.tools import (
    soundcloud_search_profiles_tool,
    soundcloud_get_profile_tool,
)

logger = logging.getLogger(__name__)


def create_mcp_server() -> Server:
    server = Server("techno-scraper")

    @server.list_tools()
    async def list_tools() -> list[Any]:
        return [
            soundcloud_search_profiles_tool,
            soundcloud_get_profile_tool,
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        if name == "soundcloud_search_profiles":
            from app.mcp.tools.soundcloud_tools import execute_soundcloud_search
            result = await execute_soundcloud_search(**arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]

        elif name == "soundcloud_get_profile":
            from app.mcp.tools.soundcloud_tools import execute_soundcloud_get_profile
            result = await execute_soundcloud_get_profile(**arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]

        else:
            raise ValueError(f"Unknown tool: {name}")

    return server


mcp_server = create_mcp_server()


async def handle_sse(request):
    async with sse_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options(),
        )


routes = [
    Route("/mcp", endpoint=handle_sse),
]

app = Starlette(routes=routes)


if __name__ == "__main__":
    import uvicorn

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    port = int(os.getenv("MCP_PORT", "8080"))
    logger.info(f"Starting MCP server on http://0.0.0.0:{port}/mcp")

    uvicorn.run(app, host="0.0.0.0", port=port)
