import logging
import traceback
from typing import Any, Dict

from fastmcp import FastMCP

from mealie import MealieFetcher
from utils import format_error_response

logger = logging.getLogger("mealie-mcp")


def register_group_tools(mcp: FastMCP, mealie: MealieFetcher) -> None:
    """Register all group-related tools with the MCP server."""

    @mcp.tool()
    def get_current_group() -> str:
        """Retrieve information about the current user's group.

        Returns:
            str: Group details including id, name, slug, and other group information.
                 This includes group-wide settings, preferences, and metadata.
        """
        try:
            logger.info({"message": "Fetching current group information"})
            return mealie.get_current_group()
        except Exception as e:
            error_msg = f"Error fetching current group information: {str(e)}"
            logger.error({"message": error_msg})
            logger.debug(
                {"message": "Error traceback", "traceback": traceback.format_exc()}
            )
            return format_error_response(error_msg)
