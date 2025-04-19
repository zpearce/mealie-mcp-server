import os
from typing import List, Optional

from dotenv import load_dotenv
from fastmcp import FastMCP

from mealie_client import MealieClient

mcp = FastMCP("mealie")

load_dotenv()
MEALIE_BASE_URL = os.getenv("MEALIE_BASE_URL")
MEALIE_API_KEY = os.getenv("MEALIE_API_KEY")

mealie = MealieClient(
    base_url=MEALIE_BASE_URL,
    api_key=MEALIE_API_KEY,
)


@mcp.tool()
def get_foods() -> str:
    """Provides a paginated list of foods that can be used in recipes.

    Features include searching foods by name, specifying ordering preferences,
    and customizing pagination.

    Returns:
        str: Food items with their details including ID, name, and associated aliases.
    """
    return mealie.get_foods()


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
    return mealie.get_recipes(
        search=search,
        page=page,
        per_page=per_page,
        categories=categories,
        tags=tags,
    )


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
    return mealie.get_recipe(slug)


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
    return mealie.create_shopping_list(name=name, description=description)


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
    return mealie.update_shopping_list(
        list_id=list_id, name=name, description=description
    )


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
    return mealie.get_shopping_lists(page=page, per_page=per_page)


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
    return mealie.get_shopping_list(list_id)


if __name__ == "__main__":
    mcp.run(transport="stdio")
