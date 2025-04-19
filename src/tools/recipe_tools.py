import logging
import traceback
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from utils import format_error_response
from mealie import MealieFetcher

logger = logging.getLogger("mealie-mcp")


def register_recipe_tools(mcp: FastMCP, mealie: MealieFetcher) -> None:
    """Register all recipe-related tools with the MCP server."""

    @mcp.tool()
    def get_recipes(
        search: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """Provides a paginated list of recipes with optional filtering.

        Args:
            search: Filters recipes by name or description.
            page: Page number for pagination.
            per_page: Number of items per page.
            categories: Filter by specific recipe categories.
            tags: Filter by specific recipe tags.

        Returns:
            str: Recipe summaries with details like ID, name, description, and image information.
        """
        try:
            logger.info(
                f"Fetching recipes with search: '{search}', page: {page}, per_page: {per_page}, categories: {categories}, tags: {tags}"
            )
            return mealie.get_recipes(
                search=search,
                page=page,
                per_page=per_page,
                categories=categories,
                tags=tags,
            )
        except Exception as e:
            error_msg = f"Error fetching recipes: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)

    @mcp.tool()
    def get_recipe(slug: str) -> str:
        """Retrieve a specific recipe by its slug identifier.

        Args:
            slug: The unique text identifier for the recipe, typically found in recipe URLs
                or from get_recipes results.

        Returns:
            str: Comprehensive recipe details including ingredients, instructions,
                nutrition information, notes, and associated metadata.
        """
        try:
            logger.info(f"Fetching recipe with slug: {slug}")
            return mealie.get_recipe(slug)
        except Exception as e:
            error_msg = f"Error fetching recipe with slug '{slug}': {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)

    @mcp.tool()
    def update_recipe(slug: str, recipe_data: Dict[str, Any]) -> str:
        """Update a specific recipe by its slug identifier.

        Args:
            slug: The unique text identifier for the recipe to update, typically found in recipe URLs
                or from get_recipes results.
            recipe_data: A dictionary containing the recipe fields to update. Can include properties like
                      name, description, ingredients, instructions, nutrition, etc.

        Returns:
            str: The updated recipe details reflecting all changes.

        Example:
            To update a recipe's name and description:
            ```json
            {
              "slug": "spaghetti-bolognese",
              "recipe_data": {
                "name": "Classic Spaghetti Bolognese",
                "description": "A rich and hearty Italian meat sauce served over spaghetti.",
                "recipeCategory": ["dinner", "pasta"],
                "tags": ["italian", "beef", "family-friendly"],
                "rating": 5,
                "recipeIngredient": [
                  {"note": "", "unit": "pound", "food": "ground beef", "quantity": 1},
                  {"note": "diced", "unit": "", "food": "onion", "quantity": 1},
                  {"note": "minced", "unit": "cloves", "food": "garlic", "quantity": 3}
                ],
                "recipeInstructions": [
                  {"text": "Heat oil in a large pan over medium heat."},
                  {"text": "Add onions and cook until translucent, about 5 minutes."},
                  {"text": "Add garlic and cook for another minute."}
                ]
              }
            }
            ```

            You can also update only specific fields:
            ```json
            {
              "slug": "spaghetti-bolognese",
              "recipe_data": {
                "prepTime": 15,
                "cookTime": 45,
                "totalTime": 60,
                "performTime": 45
              }
            }
            ```
        """
        try:
            logger.info(f"Updating recipe with slug: {slug}")
            return mealie.update_recipe(slug=slug, recipe_data=recipe_data)
        except Exception as e:
            error_msg = f"Error updating recipe with slug '{slug}': {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)
