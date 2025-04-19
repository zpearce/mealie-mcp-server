import logging
from typing import Any, Dict, List, Optional

from param_builder import ParamBuilder

logger = logging.getLogger("mealie-mcp")


class RecipeMixin:
    """Mixin class for recipe-related API endpoints"""

    def get_recipes(
        self,
        search: Optional[str] = None,
        order_by: Optional[str] = None,
        order_by_null_position: Optional[str] = None,
        order_direction: Optional[str] = "desc",
        query_filter: Optional[str] = None,
        pagination_seed: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        tools: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Provides paginated list of recipes

        Args:
            search: Search term to filter recipes by name, description, etc.
            order_by: Field to order results by
            order_by_null_position: How to handle nulls in ordering ('first' or 'last')
            order_direction: Direction to order results ('asc' or 'desc')
            query_filter: Advanced query filter
            pagination_seed: Seed for consistent pagination
            page: Page number to retrieve
            per_page: Number of items per page
            categories: List of category slugs to filter by
            tags: List of tag slugs to filter by
            tools: List of tool slugs to filter by

        Returns:
            JSON response containing recipe items and pagination information
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
            "categories": categories,
            "tags": tags,
            "tools": tools,
        }

        params = ParamBuilder(param_dict).build()

        logger.info(f"Retrieving recipes with parameters: {params}")
        return self._handle_request("GET", "/api/recipes", params=params)

    def get_recipe(self, slug: str) -> Dict[str, Any]:
        """Retrieve a specific recipe by its slug

        Args:
            slug: The slug identifier of the recipe to retrieve

        Returns:
            JSON response containing all recipe details
        """
        if not slug:
            raise ValueError("Recipe slug cannot be empty")

        logger.info(f"Retrieving recipe with slug: {slug}")
        return self._handle_request("GET", f"/api/recipes/{slug}")

    def update_recipe(self, slug: str, recipe_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a specific recipe by its slug

        Args:
            slug: The slug identifier of the recipe to update
            recipe_data: Dictionary containing the recipe properties to update

        Returns:
            JSON response containing the updated recipe details
        """
        if not slug:
            raise ValueError("Recipe slug cannot be empty")
        if not recipe_data:
            raise ValueError("Recipe data cannot be empty")

        logger.info(f"Updating recipe with slug: {slug}")
        return self._handle_request("PUT", f"/api/recipes/{slug}", json=recipe_data)
