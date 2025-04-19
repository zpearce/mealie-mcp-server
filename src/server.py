import json
import logging
import os
import traceback
from typing import List, Optional

from dotenv import load_dotenv
from fastmcp import FastMCP

from mealie_client import MealieClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("mealie_mcp_server.log")],
)
logger = logging.getLogger("mealie-mcp")

mcp = FastMCP("mealie")

# Environment variable handling with validation
load_dotenv()
MEALIE_BASE_URL = os.getenv("MEALIE_BASE_URL")
MEALIE_API_KEY = os.getenv("MEALIE_API_KEY")

if not MEALIE_BASE_URL:
    logger.error("MEALIE_BASE_URL environment variable is not set")
    raise ValueError("MEALIE_BASE_URL environment variable is required")

if not MEALIE_API_KEY:
    logger.error("MEALIE_API_KEY environment variable is not set")
    raise ValueError("MEALIE_API_KEY environment variable is required")


# Error response helper function
def format_error_response(error_message: str) -> str:
    """Format error responses consistently as JSON strings."""
    error_response = {"success": False, "error": error_message}
    return json.dumps(error_response)


try:
    logger.info(f"Initializing Mealie client with base URL: {MEALIE_BASE_URL}")
    mealie = MealieClient(
        base_url=MEALIE_BASE_URL,
        api_key=MEALIE_API_KEY,
    )
except Exception as e:
    logger.error(f"Failed to initialize Mealie client: {str(e)}")
    logger.debug(traceback.format_exc())
    raise


@mcp.tool()
def get_foods() -> str:
    """Provides a paginated list of foods that can be used in recipes.

    Features include searching foods by name, specifying ordering preferences,
    and customizing pagination.

    Returns:
        str: Food items with their details including ID, name, and associated aliases.
    """
    try:
        logger.info("Fetching list of foods from Mealie")
        return mealie.get_foods()
    except Exception as e:
        error_msg = f"Error fetching foods: {str(e)}"
        logger.error(error_msg)
        logger.debug(traceback.format_exc())
        return format_error_response(error_msg)


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
        logger.info(f"Creating shopping list '{name}' with description: {description}")
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
        logger.info(f"Fetching shopping lists with page: {page}, per_page: {per_page}")
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


if __name__ == "__main__":
    try:
        logger.info("Starting Mealie MCP Server")
        mcp.run(transport="stdio")
    except Exception as e:
        logger.critical(f"Fatal error in Mealie MCP Server: {str(e)}")
        logger.debug(traceback.format_exc())
        raise
