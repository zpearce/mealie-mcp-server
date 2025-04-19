import logging
import traceback
from typing import List, Optional

from fastmcp import FastMCP

from mealie import MealieFetcher
from utils import format_error_response

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
                {
                    "message": "Fetching recipes",
                    "search": search,
                    "page": page,
                    "per_page": per_page,
                    "categories": categories,
                    "tags": tags,
                }
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
            logger.error({"message": error_msg})
            logger.debug(
                {"message": "Error traceback", "traceback": traceback.format_exc()}
            )
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
            logger.info({"message": "Fetching recipe", "slug": slug})
            return mealie.get_recipe(slug)
        except Exception as e:
            error_msg = f"Error fetching recipe with slug '{slug}': {str(e)}"
            logger.error({"message": error_msg})
            logger.debug(
                {"message": "Error traceback", "traceback": traceback.format_exc()}
            )
            return format_error_response(error_msg)
