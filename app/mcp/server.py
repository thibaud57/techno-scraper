import json
import logging
import os
from typing import Any

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import TextContent
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Mount, Route

from app.mcp.tools import (
    soundcloud_search_profiles_tool,
    soundcloud_get_profile_tool,
    beatport_search_tool,
    beatport_get_label_releases_tool,
)

logger = logging.getLogger(__name__)


def create_mcp_server() -> Server:
    server = Server("techno-scraper")

    @server.list_tools()
    async def list_tools() -> list[Any]:
        return [
            soundcloud_search_profiles_tool,
            soundcloud_get_profile_tool,
            beatport_search_tool,
            beatport_get_label_releases_tool,
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

        elif name == "beatport_search":
            from app.mcp.tools.beatport_tools import execute_beatport_search
            result = await execute_beatport_search(**arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]

        elif name == "beatport_get_label_releases":
            from app.mcp.tools.beatport_tools import execute_beatport_get_label_releases
            result = await execute_beatport_get_label_releases(**arguments)
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]

        else:
            raise ValueError(f"Unknown tool: {name}")

    return server


mcp_server = create_mcp_server()
sse_transport = SseServerTransport("/messages/")


async def handle_sse(request):
    async with sse_transport.connect_sse(
        request.scope,
        request.receive,
        request._send,
    ) as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options(),
        )
    return Response()


routes = [
    Route("/sse", endpoint=handle_sse, methods=["GET"]),
    Mount("/messages/", app=sse_transport.handle_post_message),
]

app = Starlette(routes=routes)
