import os
from typing import List, Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from mealie_client import MealieClient

mcp = FastMCP("mealie")

load_dotenv()
MEALIE_BASE_URL = os.getenv("MEALIE_BASE_URL")
MEALIE_API_KEY = os.getenv("MEALIE_API_KEY")

mealie = MealieClient(
    base_url=MEALIE_BASE_URL,
    api_key=MEALIE_API_KEY,
)


@mcp.tool(
    description="""
    Provides a paginated list of foods that can be used in recipes.
    
    Features:
    • Search foods by name
    • Specify ordering preferences
    • Customize pagination
    
    Returns food items with their details including ID, name, and associated aliases.
    """
)
def get_foods() -> str:
    """Get all foods"""
    return mealie.get_foods()


@mcp.tool(
    description="""
    Provides a paginated list of recipes with optional filtering.
    
    Parameters:
    • search: Filters recipes by name or description
    • page/per_page: Controls pagination
    • categories: Filter by specific recipe categories
    • tags: Filter by specific recipe tags
    
    Returns recipe summaries with details like ID, name, description, and image information.
    """
)
def get_recipes(
    search: Optional[str] = None,
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    categories: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
) -> str:
    """Get a list of recipes with optional filtering"""
    return mealie.get_recipes(
        search=search,
        page=page,
        per_page=per_page,
        categories=categories,
        tags=tags,
    )


@mcp.tool(
    description="""
    Retrieve a specific recipe by its slug identifier.
    
    Parameters:
    • slug: The unique text identifier for the recipe, typically found in recipe URLs 
            or from get_recipes results
    
    Returns comprehensive recipe details including:
    • Ingredients
    • Instructions
    • Nutrition information
    • Notes
    • Associated metadata
    """
)
def get_recipe(slug: str) -> str:
    """Get detailed information about a specific recipe"""
    return mealie.get_recipe(slug)


@mcp.tool(
    description="""
    Create a new shopping list in your Mealie instance.
    
    Parameters:
    • name: Required. Will be displayed as the title of your list
    • description: Optional. Provides additional context about the list's purpose,
                  such as 'Weekly grocery trip' or 'Special dinner ingredients'
    
    Returns the created shopping list details including its ID, which you'll need for 
    subsequent operations.
    """
)
def create_shopping_list(name: str, description: Optional[str] = None) -> str:
    """Create a new shopping list"""
    return mealie.create_shopping_list(name=name, description=description)


@mcp.tool(
    description="""
    Update properties of an existing shopping list.
    
    Parameters:
    • list_id: The unique identifier of the shopping list to update
              (obtained from create_shopping_list or get_shopping_lists)
    • name: If provided, replaces the current name of the list
    • description: If provided, replaces the current description
    
    Note: At least one of name or description must be provided to make meaningful changes.
    
    Returns the updated shopping list details reflecting all changes made.
    """
)
def update_shopping_list(
    list_id: str, name: Optional[str] = None, description: Optional[str] = None
) -> str:
    """Update an existing shopping list"""
    return mealie.update_shopping_list(
        list_id=list_id, name=name, description=description
    )


@mcp.tool(
    description="""
    Get a list of all shopping lists in your Mealie instance with pagination support.
    
    Parameters:
    • page: Page number to retrieve (starts at 1)
    • per_page: Number of items included in each response
    
    Returns:
    • Array of shopping list objects with their details (ID, name, description, etc.)
    • Pagination information
    """
)
def get_shopping_lists(
    page: Optional[int] = None, per_page: Optional[int] = None
) -> str:
    """Get all shopping lists"""
    return mealie.get_shopping_lists(page=page, per_page=per_page)


@mcp.tool(
    description="""
    Get detailed information about a specific shopping list, including all its items.
    
    Parameters:
    • list_id: The unique identifier of the shopping list to retrieve
              (obtained from create_shopping_list or get_shopping_lists)
    
    Returns complete shopping list details including:
    • Basic metadata (ID, name, description, creation date)
    • Shopping list items with quantities and checked status
    • Any associated recipe references
    • Label settings
    """
)
def get_shopping_list(list_id: str) -> str:
    """Get a specific shopping list by ID"""
    return mealie.get_shopping_list(list_id)


if __name__ == "__main__":
    mcp.run(transport="stdio")
