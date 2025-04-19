import logging
import traceback
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from utils import format_error_response
from mealie import MealieFetcher

logger = logging.getLogger("mealie-mcp")


def register_shopping_list_tools(mcp: FastMCP, mealie: MealieFetcher) -> None:
    """Register all shopping list-related tools with the MCP server."""

    @mcp.tool()
    def create_shopping_list(name: str, description: Optional[str] = None) -> str:
        """Create a new shopping list in your Mealie instance.

        Args:
            name: Required. Will be displayed as the title of your list.
            description: Provides additional context about the list's purpose,
                such as 'Weekly grocery trip' or 'Special dinner ingredients'.

        Returns:
            str: The created shopping list details including its ID, which you'll need for
                subsequent operations.
        """
        try:
            logger.info(
                f"Creating shopping list '{name}' with description: {description}"
            )
            return mealie.create_shopping_list(name=name, description=description)
        except Exception as e:
            error_msg = f"Error creating shopping list '{name}': {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)

    @mcp.tool()
    def update_shopping_list(
        list_id: str, name: Optional[str] = None, description: Optional[str] = None
    ) -> str:
        """Update properties of an existing shopping list.

        Args:
            list_id: The unique identifier of the shopping list to update
                (obtained from create_shopping_list or get_shopping_lists).
            name: If provided, replaces the current name of the list.
            description: If provided, replaces the current description.

        Note:
            At least one of name or description must be provided to make meaningful changes.

        Returns:
            str: The updated shopping list details reflecting all changes made.
        """
        try:
            logger.info(
                f"Updating shopping list {list_id} with name: {name}, description: {description}"
            )
            return mealie.update_shopping_list(
                list_id=list_id, name=name, description=description
            )
        except Exception as e:
            error_msg = f"Error updating shopping list '{list_id}': {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)

    @mcp.tool()
    def get_shopping_lists(
        page: Optional[int] = None, per_page: Optional[int] = None
    ) -> str:
        """Get a list of all shopping lists in your Mealie instance with pagination support.

        Args:
            page: Page number to retrieve (starts at 1).
            per_page: Number of items included in each response.

        Returns:
            str: Array of shopping list objects with their details (ID, name, description, etc.)
                and pagination information.
        """
        try:
            logger.info(
                f"Fetching shopping lists with page: {page}, per_page: {per_page}"
            )
            return mealie.get_shopping_lists(page=page, per_page=per_page)
        except Exception as e:
            error_msg = f"Error fetching shopping lists: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)

    @mcp.tool()
    def get_shopping_list(list_id: str) -> str:
        """Get detailed information about a specific shopping list, including all its items.

        Args:
            list_id: The unique identifier of the shopping list to retrieve
                (obtained from create_shopping_list or get_shopping_lists).

        Returns:
            str: Complete shopping list details including basic metadata (ID, name, description,
                creation date), shopping list items with quantities and checked status,
                any associated recipe references, and label settings.
        """
        try:
            logger.info(f"Fetching shopping list with ID: {list_id}")
            return mealie.get_shopping_list(list_id)
        except Exception as e:
            error_msg = f"Error fetching shopping list '{list_id}': {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)

    @mcp.tool()
    def create_shopping_list_item(
        list_id: str,
        item_name: str,
        quantity: Optional[float] = None,
        unit: Optional[str] = None,
        note: Optional[str] = None,
        food_id: Optional[str] = None,
    ) -> str:
        """Add a new item to a shopping list.

        Args:
            list_id: The unique identifier of the shopping list to add the item to.
            item_name: Required name of the item to add to the list.
            quantity: Optional numeric amount of the item.
            unit: Optional unit of measurement (e.g., "cup", "tablespoon", "oz").
            note: Optional additional information about the item.
            food_id: Optional reference to a food item in the Mealie database.

        Returns:
            str: The created shopping list item details including its ID and
                association with the specified shopping list.
        """
        try:
            logger.info(f"Creating item '{item_name}' in shopping list {list_id}")
            return mealie.create_shopping_list_item(
                list_id=list_id,
                item_name=item_name,
                quantity=quantity,
                unit=unit,
                note=note,
                food_id=food_id,
            )
        except Exception as e:
            error_msg = f"Error creating shopping list item '{item_name}': {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)

    @mcp.tool()
    def update_shopping_list_item(
        item_id: str,
        item_name: Optional[str] = None,
        quantity: Optional[float] = None,
        unit: Optional[str] = None,
        note: Optional[str] = None,
        checked: Optional[bool] = None,
        position: Optional[int] = None,
    ) -> str:
        """Update an existing shopping list item.

        Args:
            item_id: The unique identifier of the item to update.
            item_name: New display name for the item.
            quantity: New quantity value.
            unit: New unit of measurement.
            note: New note or additional details.
            checked: Whether the item is marked as completed/purchased.
            position: New sorting position in the list.

        Returns:
            str: The updated shopping list item details reflecting all changes made.

        Note:
            You must provide at least one parameter other than item_id to make meaningful changes.
        """
        try:
            logger.info(f"Updating shopping list item {item_id}")
            return mealie.update_shopping_list_item(
                item_id=item_id,
                item_name=item_name,
                quantity=quantity,
                unit=unit,
                note=note,
                checked=checked,
                position=position,
            )
        except Exception as e:
            error_msg = f"Error updating shopping list item '{item_id}': {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)

    @mcp.tool()
    def delete_shopping_list_item(item_id: str) -> str:
        """Remove an item from a shopping list.

        Args:
            item_id: The unique identifier of the shopping list item to delete.

        Returns:
            str: Confirmation of successful deletion.
        """
        try:
            logger.info(f"Deleting shopping list item {item_id}")
            return mealie.delete_shopping_list_item(item_id)
        except Exception as e:
            error_msg = f"Error deleting shopping list item '{item_id}': {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)

    @mcp.tool()
    def get_shopping_list_item(item_id: str) -> str:
        """Retrieve details about a specific shopping list item.

        Args:
            item_id: The unique identifier of the shopping list item to retrieve.

        Returns:
            str: Complete item details including name, quantity, unit, notes,
                checked status, and position in the list.
        """
        try:
            logger.info(f"Fetching shopping list item with ID: {item_id}")
            return mealie.get_shopping_list_item(item_id)
        except Exception as e:
            error_msg = f"Error fetching shopping list item '{item_id}': {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)

    @mcp.tool()
    def toggle_shopping_list_item(item_id: str) -> str:
        """Toggle the checked/completed status of a shopping list item.

        Args:
            item_id: The unique identifier of the shopping list item to toggle.

        Returns:
            str: Updated shopping list item details with the new checked status.
        """
        try:
            logger.info(f"Toggling checked status for shopping list item {item_id}")
            return mealie.toggle_shopping_list_item(item_id)
        except Exception as e:
            error_msg = f"Error toggling shopping list item '{item_id}': {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)

    @mcp.tool()
    def bulk_create_shopping_list_items(
        list_id: str, items: List[Dict[str, Any]]
    ) -> str:
        """Add multiple items to a shopping list in a single operation.

        Args:
            list_id: The unique identifier of the shopping list to add items to.
            items: A list of item dictionaries, where each dictionary must contain at least
                a 'display' key with the item name, and can optionally include 'quantity',
                'unit', 'note', and 'foodId'.

        Returns:
            str: The created shopping list items details.

        Example:
            To add multiple items, provide a list of dictionaries like:
            [
                {"display": "Milk", "quantity": 1, "unit": "gallon"},
                {"display": "Eggs", "quantity": 12},
                {"display": "Bread"}
            ]
        """
        try:
            logger.info(f"Bulk creating {len(items)} items in shopping list {list_id}")
            return mealie.bulk_create_shopping_list_items(list_id=list_id, items=items)
        except Exception as e:
            error_msg = f"Error bulk creating shopping list items: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)

    @mcp.tool()
    def bulk_update_shopping_list_items(items: List[Dict[str, Any]]) -> str:
        """Update multiple shopping list items in a single operation.

        Args:
            items: A list of item dictionaries, where each dictionary must contain at least
                an 'id' key with the item ID, and the fields to update such as 'display',
                'quantity', 'unit', 'note', 'checked', or 'position'.

        Returns:
            str: The updated shopping list items details.

        Example:
            To update multiple items, provide a list of dictionaries like:
            [
                {"id": "item1-id", "display": "Whole Milk", "checked": true},
                {"id": "item2-id", "quantity": 6, "note": "Large brown eggs"}
            ]
        """
        try:
            logger.info(f"Bulk updating {len(items)} shopping list items")
            return mealie.bulk_update_shopping_list_items(items=items)
        except Exception as e:
            error_msg = f"Error bulk updating shopping list items: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)

    @mcp.tool()
    def bulk_delete_shopping_list_items(item_ids: List[str]) -> str:
        """Delete multiple shopping list items in a single operation.

        Args:
            item_ids: A list of shopping list item IDs to delete.

        Returns:
            str: Confirmation of successful deletion.

        Example:
            To delete multiple items, provide a list of item IDs:
            ["item1-id", "item2-id", "item3-id"]
        """
        try:
            logger.info(f"Bulk deleting {len(item_ids)} shopping list items")
            return mealie.bulk_delete_shopping_list_items(item_ids=item_ids)
        except Exception as e:
            error_msg = f"Error bulk deleting shopping list items: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)

    @mcp.tool()
    def get_all_shopping_list_items(
        list_id: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        order_by: Optional[str] = None,
        order_direction: Optional[str] = None,
    ) -> str:
        """Retrieve all shopping list items, optionally filtered by shopping list ID.

        Args:
            list_id: Optional ID of a specific shopping list to filter items.
            page: Page number for pagination.
            per_page: Number of items to return per page.
            order_by: Field to sort results by (e.g., 'position', 'display').
            order_direction: Sort order ('asc' or 'desc').

        Returns:
            str: List of shopping list items and pagination information.
        """
        try:
            logger.info(f"Retrieving all shopping list items with list_id: {list_id}")
            return mealie.get_all_shopping_list_items(
                list_id=list_id,
                page=page,
                per_page=per_page,
                order_by=order_by,
                order_direction=order_direction,
            )
        except Exception as e:
            error_msg = f"Error retrieving shopping list items: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)
