import logging
from typing import Any, Dict, List, Optional

from param_builder import ParamBuilder

logger = logging.getLogger("mealie-mcp")


class ShoppingListMixin:
    """Mixin class for shopping list-related API endpoints"""

    def create_shopping_list(
        self, name: str, description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new shopping list

        Args:
            name: The name of the shopping list
            description: Optional description for the shopping list

        Returns:
            JSON response containing the created shopping list details
        """
        if not name:
            raise ValueError("Shopping list name cannot be empty")

        payload = {"name": name}

        if description is not None:
            payload["description"] = description

        logger.info(f"Creating shopping list with name: {name}")
        return self._handle_request(
            "POST", "/api/households/shopping/lists", json=payload
        )

    def update_shopping_list(
        self,
        list_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing shopping list

        Args:
            list_id: The ID of the shopping list to update
            name: New name for the shopping list
            description: New description for the shopping list

        Returns:
            JSON response containing the updated shopping list details
        """
        if not list_id:
            raise ValueError("Shopping list ID cannot be empty")

        if name is None and description is None:
            raise ValueError("At least one of name or description must be provided")

        payload = {"id": list_id}

        if name is not None:
            payload["name"] = name

        if description is not None:
            payload["description"] = description

        logger.info(f"Updating shopping list {list_id}")
        return self._handle_request(
            "PUT", f"/api/households/shopping/lists/{list_id}", json=payload
        )

    def get_shopping_lists(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        pagination_seed: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Retrieve all shopping lists

        Args:
            page: Page number to retrieve
            per_page: Number of items per page
            pagination_seed: Seed for consistent pagination

        Returns:
            JSON response containing shopping list items and pagination information
        """

        param_dict = {
            "page": page,
            "perPage": per_page,
            "paginationSeed": pagination_seed,
        }

        params = ParamBuilder(param_dict).build()

        logger.info(f"Retrieving shopping lists with parameters: {params}")
        return self._handle_request(
            "GET", "/api/households/shopping/lists", params=params
        )

    def get_shopping_list(self, list_id: str) -> Dict[str, Any]:
        """Retrieve a specific shopping list by ID

        Args:
            list_id: The ID of the shopping list to retrieve

        Returns:
            JSON response containing the shopping list details
        """
        if not list_id:
            raise ValueError("Shopping list ID cannot be empty")

        logger.info(f"Retrieving shopping list with ID: {list_id}")
        return self._handle_request("GET", f"/api/households/shopping/lists/{list_id}")

    def create_shopping_list_item(
        self,
        list_id: str,
        item_name: str,
        quantity: Optional[float] = None,
        unit: Optional[str] = None,
        note: Optional[str] = None,
        food_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new shopping list item

        Args:
            list_id: The ID of the shopping list to add the item to
            item_name: The name of the item
            quantity: Optional quantity of the item
            unit: Optional unit of measurement
            note: Optional notes about the item
            food_id: Optional ID of a food in the database

        Returns:
            JSON response containing the created shopping list item details
        """
        if not list_id:
            raise ValueError("Shopping list ID cannot be empty")
        if not item_name:
            raise ValueError("Item name cannot be empty")

        payload = {"shoppingListId": list_id, "display": item_name}

        if quantity is not None:
            payload["quantity"] = quantity
        if unit is not None:
            payload["unit"] = unit
        if note is not None:
            payload["note"] = note
        if food_id is not None:
            payload["foodId"] = food_id

        logger.info(f"Creating item '{item_name}' in shopping list {list_id}")
        return self._handle_request("POST", "/api/shopping/items", json=payload)

    def update_shopping_list_item(
        self,
        item_id: str,
        item_name: Optional[str] = None,
        quantity: Optional[float] = None,
        unit: Optional[str] = None,
        note: Optional[str] = None,
        checked: Optional[bool] = None,
        position: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Update an existing shopping list item

        Args:
            item_id: The ID of the shopping list item to update
            item_name: New name for the item
            quantity: New quantity for the item
            unit: New unit of measurement for the item
            note: New notes for the item
            checked: Whether the item is checked off
            position: Position of the item in the list

        Returns:
            JSON response containing the updated shopping list item details
        """
        if not item_id:
            raise ValueError("Shopping list item ID cannot be empty")

        if all(
            param is None
            for param in [item_name, quantity, unit, note, checked, position]
        ):
            raise ValueError("At least one parameter must be provided to update")

        payload = {"id": item_id}

        if item_name is not None:
            payload["display"] = item_name
        if quantity is not None:
            payload["quantity"] = quantity
        if unit is not None:
            payload["unit"] = unit
        if note is not None:
            payload["note"] = note
        if checked is not None:
            payload["checked"] = checked
        if position is not None:
            payload["position"] = position

        logger.info(f"Updating shopping list item {item_id}")
        return self._handle_request(
            "PUT", f"/api/shopping/items/{item_id}", json=payload
        )

    def delete_shopping_list_item(self, item_id: str) -> Dict[str, Any]:
        """Delete a shopping list item

        Args:
            item_id: The ID of the shopping list item to delete

        Returns:
            JSON response confirming deletion
        """
        if not item_id:
            raise ValueError("Shopping list item ID cannot be empty")

        logger.info(f"Deleting shopping list item {item_id}")
        return self._handle_request("DELETE", f"/api/shopping/items/{item_id}")

    def get_shopping_list_item(self, item_id: str) -> Dict[str, Any]:
        """Retrieve a specific shopping list item by ID

        Args:
            item_id: The ID of the shopping list item to retrieve

        Returns:
            JSON response containing the shopping list item details
        """
        if not item_id:
            raise ValueError("Shopping list item ID cannot be empty")

        logger.info(f"Retrieving shopping list item with ID: {item_id}")
        return self._handle_request("GET", f"/api/shopping/items/{item_id}")

    def toggle_shopping_list_item(self, item_id: str) -> Dict[str, Any]:
        """Toggle the checked status of a shopping list item

        Args:
            item_id: The ID of the shopping list item to toggle

        Returns:
            JSON response containing the updated shopping list item details
        """
        if not item_id:
            raise ValueError("Shopping list item ID cannot be empty")

        logger.info(f"Toggling checked status for shopping list item {item_id}")
        return self._handle_request("PUT", f"/api/shopping/items/{item_id}/toggle")

    def bulk_create_shopping_list_items(
        self, list_id: str, items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create multiple shopping list items at once

        Args:
            list_id: The ID of the shopping list to add the items to
            items: List of item dictionaries, each containing at least a display name
                   and optionally quantity, unit, note, and food_id

        Returns:
            JSON response containing the created shopping list items
        """
        if not list_id:
            raise ValueError("Shopping list ID cannot be empty")
        if not items or not isinstance(items, list):
            raise ValueError("Items must be a non-empty list of item dictionaries")

        # Ensure each item has the shopping list ID and required fields
        payload = []
        for item in items:
            if not item.get("display"):
                raise ValueError("Each item must have a 'display' name")

            item_payload = {"shoppingListId": list_id, "display": item["display"]}

            # Add optional fields if present
            if "quantity" in item:
                item_payload["quantity"] = item["quantity"]
            if "unit" in item:
                item_payload["unit"] = item["unit"]
            if "note" in item:
                item_payload["note"] = item["note"]
            if "foodId" in item:
                item_payload["foodId"] = item["foodId"]

            payload.append(item_payload)

        logger.info(f"Bulk creating {len(items)} items in shopping list {list_id}")
        return self._handle_request("POST", "/api/shopping/items/bulk", json=payload)

    def bulk_update_shopping_list_items(
        self, items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Update multiple shopping list items at once

        Args:
            items: List of item dictionaries, each containing at least the item ID
                  and the fields to update (display, quantity, unit, note, checked, position)

        Returns:
            JSON response containing the updated shopping list items
        """
        if not items or not isinstance(items, list):
            raise ValueError("Items must be a non-empty list of item dictionaries")

        # Validate that each item has the required ID
        for item in items:
            if not item.get("id"):
                raise ValueError("Each item must have an 'id' field")

        logger.info(f"Bulk updating {len(items)} shopping list items")
        return self._handle_request("PUT", "/api/shopping/items/bulk", json=items)

    def bulk_delete_shopping_list_items(self, item_ids: List[str]) -> Dict[str, Any]:
        """Delete multiple shopping list items at once

        Args:
            item_ids: List of shopping list item IDs to delete

        Returns:
            JSON response confirming deletion
        """
        if not item_ids or not isinstance(item_ids, list):
            raise ValueError("Item IDs must be a non-empty list")

        logger.info(f"Bulk deleting {len(item_ids)} shopping list items")
        return self._handle_request("DELETE", "/api/shopping/items/bulk", json=item_ids)

    def get_all_shopping_list_items(
        self,
        list_id: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        pagination_seed: Optional[str] = None,
        order_by: Optional[str] = None,
        order_direction: Optional[str] = None,
        query_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Retrieve all shopping list items, optionally filtered by list ID

        Args:
            list_id: Optional ID of a shopping list to filter items
            page: Page number to retrieve
            per_page: Number of items per page
            pagination_seed: Seed for consistent pagination
            order_by: Field to order results by
            order_direction: Direction to order results ('asc' or 'desc')
            query_filter: Advanced query filter

        Returns:
            JSON response containing shopping list items and pagination information
        """

        param_dict = {
            "shoppingListId": list_id,
            "page": page,
            "perPage": per_page,
            "paginationSeed": pagination_seed,
            "orderBy": order_by,
            "orderDirection": order_direction,
            "queryFilter": query_filter,
        }

        params = ParamBuilder(param_dict).build()

        logger.info(f"Retrieving all shopping list items with parameters: {params}")
        return self._handle_request("GET", "/api/shopping/items", params=params)
