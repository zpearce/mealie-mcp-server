import logging
import traceback
from typing import Any, Dict

from fastmcp import FastMCP

from mealie import MealieFetcher
from utils import format_error_response

logger = logging.getLogger("mealie-mcp")


def register_user_tools(mcp: FastMCP, mealie: MealieFetcher) -> None:
    """Register all user-related tools with the MCP server."""

    @mcp.tool()
    def get_current_user() -> str:
        """Retrieve information about the currently logged-in user.

        Returns:
            str: User details including id, username, email, name, and other profile information.
                 This includes permissions, preferences, and API tokens associated with the user.
        """
        try:
            logger.info({"message": "Fetching current user information"})
            return mealie.get_current_user()
        except Exception as e:
            error_msg = f"Error fetching current user information: {str(e)}"
            logger.error({"message": error_msg})
            logger.debug(
                {"message": "Error traceback", "traceback": traceback.format_exc()}
            )
            return format_error_response(error_msg)
