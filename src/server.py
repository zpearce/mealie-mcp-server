import logging
import os
import traceback

from dotenv import load_dotenv
from fastmcp import FastMCP

from mealie import MealieFetcher
from tools import register_all_tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("mealie_mcp_server.log")],
)
logger = logging.getLogger("mealie-mcp")

mcp = FastMCP("mealie")


load_dotenv()
MEALIE_BASE_URL = os.getenv("MEALIE_BASE_URL")
MEALIE_API_KEY = os.getenv("MEALIE_API_KEY")
if not MEALIE_BASE_URL or not MEALIE_API_KEY:
    raise ValueError(
        "MEALIE_BASE_URL and MEALIE_API_KEY must be set in environment variables."
    )

try:
    mealie = MealieFetcher(
        base_url=MEALIE_BASE_URL,
        api_key=MEALIE_API_KEY,
    )
except Exception as e:
    logger.error(f"Failed to initialize Mealie client: {str(e)}")
    logger.debug(traceback.format_exc())
    raise

register_all_tools(mcp, mealie)

if __name__ == "__main__":
    try:
        logger.info("Starting Mealie MCP Server")
        mcp.run(transport="stdio")
    except Exception as e:
        logger.critical(f"Fatal error in Mealie MCP Server: {str(e)}")
        logger.debug(traceback.format_exc())
        raise
