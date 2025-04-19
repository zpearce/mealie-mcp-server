import logging
from typing import Any, Dict, Optional

from mealie.client import MealieClient
from utils import format_api_params

logger = logging.getLogger("mealie-mcp")


class FoodMixin(MealieClient):

    def get_foods(
        self,
        search: Optional[str] = None,
        order_by: Optional[str] = None,
        order_by_null_position: Optional[str] = None,
        order_direction: Optional[str] = "desc",
        query_filter: Optional[str] = None,
        pagination_seed: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Provides paginated list of foods

        Args:
            search: Search term to filter foods by name
            order_by: Field to order results by
            order_by_null_position: How to handle nulls in ordering ('first' or 'last')
            order_direction: Direction to order results ('asc' or 'desc')
            query_filter: Advanced query filter
            pagination_seed: Seed for consistent pagination
            page: Page number to retrieve
            per_page: Number of items per page

        Returns:
            JSON response containing food items and pagination information
        """

        param_dict = {
            "search": search,
            "orderBy": order_by,
            "orderByNullPosition": order_by_null_position,
            "orderDirection": order_direction,
            "queryFilter": query_filter,
            "paginationSeed": pagination_seed,
            "page": page,
            "perPage": per_page,
        }

        params = format_api_params(param_dict)

        logger.info(f"Retrieving foods with parameters: {params}")
        return self._handle_request("GET", "/api/foods", params=params)

    def get_food(self, food_id: str) -> Dict[str, Any]:
        """Get a specific food by ID

        Args:
            food_id: The UUID of the food to retrieve

        Returns:
            JSON response containing food details
        """
        logger.info(f"Retrieving food with ID: {food_id}")
        return self._handle_request("GET", f"/api/foods/{food_id}")

    def create_food(self, food_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new food item

        Args:
            food_data: Dictionary containing food details such as name, description, and aliases

        Returns:
            JSON response containing the created food details
        """
        logger.info(f"Creating new food: {food_data.get('name', 'Unknown')}")
        return self._handle_request("POST", "/api/foods", json=food_data)

    def update_food(self, food_id: str, food_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing food item

        Args:
            food_id: The UUID of the food to update
            food_data: Dictionary containing updated food details

        Returns:
            JSON response containing the updated food details
        """
        logger.info(f"Updating food with ID: {food_id}")
        return self._handle_request("PUT", f"/api/foods/{food_id}", json=food_data)
