import logging
import os
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

if __name__ == "__main__":
    port = int(os.getenv("MCP_PORT", "8080"))
    logging.info(f"Starting MCP server on http://0.0.0.0:{port}/sse")

    uvicorn.run("app.mcp.server:app", host="0.0.0.0", port=port, log_level="info")
