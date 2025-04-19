import os
from dotenv import load_dotenv
from mealie_client import MealieClient
from mcp.server.fastmcp import FastMCP
from typing import Optional, List

mcp = FastMCP("mealie")

load_dotenv()
MEALIE_BASE_URL = os.getenv("MEALIE_BASE_URL")
MEALIE_API_KEY = os.getenv("MEALIE_API_KEY")

mealie = MealieClient(
    base_url=MEALIE_BASE_URL,
    api_key=MEALIE_API_KEY,
)


@mcp.tool(description="Provides paginated list of foods that can be used in recipes")
def get_foods() -> str:
    return mealie.get_foods()


@mcp.tool(description="Provides paginated list of recipes with optional filtering")
def get_recipes(
    search: Optional[str] = None,
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    categories: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
) -> str:
    """Get a list of recipes with optional filtering

    Args:
        search: Search term to filter recipes by name, description, etc.
        page: Page number to retrieve
        per_page: Number of items per page
        categories: List of category slugs to filter by
        tags: List of tag slugs to filter by

    Returns:
        JSON response containing recipe items and pagination information
    """
    return mealie.get_recipes(
        search=search,
        page=page,
        per_page=per_page,
        categories=categories,
        tags=tags,
    )


@mcp.tool(description="Retrieve a specific recipe by its slug identifier")
def get_recipe(slug: str) -> str:
    """Get detailed information about a specific recipe

    Args:
        slug: The slug identifier of the recipe to retrieve

    Returns:
        JSON response containing all recipe details
    """
    return mealie.get_recipe(slug)


if __name__ == "__main__":
    mcp.run(transport="stdio")
