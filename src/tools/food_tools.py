import logging
import traceback
from typing import Any, Dict, Optional

from fastmcp import FastMCP

from errors import format_error_response
from mealie import MealieFetcher

logger = logging.getLogger("mealie-mcp")


def register_food_tools(mcp: FastMCP, mealie: MealieFetcher) -> None:
    """Register all food-related tools with the MCP server."""

    @mcp.tool()
    def get_foods(
        search: Optional[str] = None,
        order_by: Optional[str] = None,
        order_direction: Optional[str] = "desc",
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> str:
        """Provides a paginated list of foods that can be used in recipes.

        Features include searching foods by name, specifying ordering preferences,
        and customizing pagination.

        Args:
            search: Search term to filter foods by name
            order_by: Field to order results by
            order_direction: Direction to order results ('asc' or 'desc')
            page: Page number to retrieve
            per_page: Number of items per page

        Returns:
            str: Food items with their details including ID, name, and associated aliases.
        """
        try:
            logger.info("Fetching list of foods from Mealie")
            return mealie.get_foods(
                search=search,
                order_by=order_by,
                order_direction=order_direction,
                page=page,
                per_page=per_page,
            )
        except Exception as e:
            error_msg = f"Error fetching foods: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)

    @mcp.tool()
    def get_food(food_id: str) -> str:
        """Get a specific food by ID.

        Args:
            food_id: The UUID of the food to retrieve

        Returns:
            str: Food details including ID, name, description, and associated aliases.
        """
        try:
            logger.info(f"Fetching food with ID {food_id} from Mealie")
            return mealie.get_food(food_id)
        except Exception as e:
            error_msg = f"Error fetching food with ID {food_id}: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)

    @mcp.tool()
    def create_food(food_data: Dict[str, Any]) -> str:
        """Create a new food item.

        Args:
            food_data: Dictionary containing food details such as name, description, and aliases

        Returns:
            str: Created food details including the assigned ID.
        """
        try:
            logger.info(f"Creating new food: {food_data.get('name', 'Unknown')}")
            return mealie.create_food(food_data)
        except Exception as e:
            error_msg = f"Error creating food: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)

    @mcp.tool()
    def update_food(food_id: str, food_data: Dict[str, Any]) -> str:
        """Update an existing food item.

        Args:
            food_id: The UUID of the food to update
            food_data: Dictionary containing updated food details

        Returns:
            str: Updated food details.
        """
        try:
            logger.info(f"Updating food with ID {food_id}")
            return mealie.update_food(food_id, food_data)
        except Exception as e:
            error_msg = f"Error updating food with ID {food_id}: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)
