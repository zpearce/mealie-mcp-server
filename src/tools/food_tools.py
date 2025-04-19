import logging
import traceback

from fastmcp import FastMCP

from errors import format_error_response
from mealie import MealieFetcher

logger = logging.getLogger("mealie-mcp")


def register_food_tools(mcp: FastMCP, mealie: MealieFetcher) -> None:
    """Register all food-related tools with the MCP server."""

    @mcp.tool()
    def get_foods() -> str:
        """Provides a paginated list of foods that can be used in recipes.

        Features include searching foods by name, specifying ordering preferences,
        and customizing pagination.

        Returns:
            str: Food items with their details including ID, name, and associated aliases.
        """
        try:
            logger.info("Fetching list of foods from Mealie")
            return mealie.get_foods()
        except Exception as e:
            error_msg = f"Error fetching foods: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)
