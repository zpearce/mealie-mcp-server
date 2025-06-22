import logging
import traceback
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from mealie import MealieFetcher
from models.recipe import Recipe, RecipeIngredient, RecipeInstruction
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
    def get_recipe_detailed(slug: str) -> str:
        """Retrieve a specific recipe by its slug identifier. Use this when to get full recipe
        details for tasks like updating or displaying the recipe.

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

    @mcp.tool()
    def get_recipe_concise(slug: str) -> str:
        """Retrieve a concise version of a specific recipe by its slug identifier. Use this when you only
        need a summary of the recipe, such as for when mealplaning.

        Args:
            slug: The unique text identifier for the recipe, typically found in recipe URLs
                or from get_recipes results.


        """
        try:
            logger.info({"message": "Fetching recipe", "slug": slug})
            recipe_json = mealie.get_recipe(slug)
            recipe = Recipe.model_validate(recipe_json)
            return recipe.model_dump(
                include={
                    "name",
                    "slug",
                    "recipeServings",
                    "recipeYieldQuantity",
                    "recipeYield",
                    "totalTime",
                    "rating",
                      "recipeIngredient",
                    "lastMade",
                },
                exclude_none=True,
            )
        except Exception as e:
            error_msg = f"Error fetching recipe with slug '{slug}': {str(e)}"
            logger.error({"message": error_msg})
            logger.debug(
                {"message": "Error traceback", "traceback": traceback.format_exc()}
            )
            return format_error_response(error_msg)

    @mcp.tool()
    def create_recipe(
        name: str, ingredients: list[str], instructions: list[str]
    ) -> str:
        """Create a new recipe

        Args:
            name: The name of the new recipe to be created.
            ingredients: A list of ingredients for the recipe include quantities and units.
            instructions: A list of instructions for preparing the recipe.

        Returns:
            str: Confirmation message or details about the created recipe.
        """
        try:
            logger.info({"message": "Creating recipe", "name": name})
            slug = mealie.create_recipe(name)
            recipe_json = mealie.get_recipe(slug)
            recipe = Recipe.model_validate(recipe_json)
            recipe.recipeIngredient = [RecipeIngredient(note=i) for i in ingredients]
            recipe.recipeInstructions = [
                RecipeInstruction(text=i) for i in instructions
            ]
            return mealie.update_recipe(slug, recipe.model_dump(exclude_none=True))
        except Exception as e:
            error_msg = f"Error creating recipe '{name}': {str(e)}"
            logger.error({"message": error_msg})
            logger.debug(
                {"message": "Error traceback", "traceback": traceback.format_exc()}
            )
            return format_error_response(error_msg)

    @mcp.tool()
    def update_recipe(
        slug: str,
        ingredients: list[str],
        instructions: list[str],
        name: Optional[str] = None,
        tags: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        description: Optional[str] = None,
        recipe_servings: Optional[float] = None,
        recipe_yield: Optional[str] = None,
        prep_time: Optional[str] = None,
        cook_time: Optional[str] = None,
        total_time: Optional[str] = None,
        extras: Optional[Dict[str, Any]] = None,
        nutrition: Optional[Dict[str, str]] = None,
        tools: Optional[List[str]] = None,
        settings: Optional[Dict[str, bool]] = None,
        org_url: Optional[str] = None,
    ) -> str:
        """Updates an existing recipe with comprehensive field support.

        Args:
            slug: The unique text identifier for the recipe to be updated.
            ingredients: A list of ingredients for the recipe include quantities and units.
            instructions: A list of instructions for preparing the recipe.
            name: New name for the recipe (optional).
            tags: List of tag slugs for categorizing the recipe (e.g., ["ww-points-5", "family-favorite"]).
            categories: List of category slugs (e.g., ["dinner", "italian"]).
            description: Recipe description or overview.
            recipe_servings: Number of servings the recipe makes (as float).
            recipe_yield: Text description of yield (e.g., "6 servings").
            prep_time: Preparation time in minutes (as string).
            cook_time: Cooking time in minutes (as string).
            total_time: Total time in minutes (as string).
            extras: Custom metadata dictionary for tracking (e.g., {"last_cooked": "2024-01-15", "ww_points": 7}).
            nutrition: Nutrition information dictionary (calories, proteinContent, etc.).
            tools: List of tool slugs required for the recipe.
            settings: Recipe display settings (public, showNutrition, etc.).
            org_url: Original source URL of the recipe.

        Returns:
            str: Confirmation message or details about the updated recipe.
        """
        try:
            logger.info({"message": "Updating recipe", "slug": slug})
            recipe_json = mealie.get_recipe(slug)
            recipe = Recipe.model_validate(recipe_json)

            recipe.recipeIngredient = [RecipeIngredient(note=i) for i in ingredients]
            recipe.recipeInstructions = [
                RecipeInstruction(text=i) for i in instructions
            ]

            if name is not None:
                recipe.name = name
            if tags is not None:
                recipe.tags = tags
            if categories is not None:
                recipe.recipeCategory = categories
            if description is not None:
                recipe.description = description
            if recipe_servings is not None:
                recipe.recipeServings = recipe_servings
            if recipe_yield is not None:
                recipe.recipeYield = recipe_yield
            if prep_time is not None:
                recipe.prepTime = prep_time
            if cook_time is not None:
                recipe.cookTime = cook_time
            if total_time is not None:
                recipe.totalTime = total_time
            if extras is not None:
                recipe.extras = extras
            if nutrition is not None:
                from models.recipe import RecipeNutrition
                recipe.nutrition = RecipeNutrition(**nutrition)
            if tools is not None:
                recipe.tools = tools
            if settings is not None:
                from models.recipe import RecipeSettings
                recipe.settings = RecipeSettings(**settings)
            if org_url is not None:
                recipe.orgURL = org_url

            return mealie.update_recipe(slug, recipe.model_dump(exclude_none=True))
        except Exception as e:
            error_msg = f"Error updating recipe '{slug}': {str(e)}"
            logger.error({"message": error_msg})
            logger.debug(
                {"message": "Error traceback", "traceback": traceback.format_exc()}
            )
            return format_error_response(error_msg)

    @mcp.tool()
    def import_recipe_from_url(url: str) -> str:
        """Import a recipe from a URL using Mealie's built-in scraper.

        Args:
            url: The URL of the recipe to import.

        Returns:
            str: JSON response containing the imported recipe details.
        """
        try:
            logger.info({"message": "Importing recipe from URL", "url": url})

            if not url:
                return {"success": False, "error": "URL cannot be empty"}
            if not url.startswith(('http://', 'https://')):
                return {"success": False, "error": "Invalid URL format"}

            return mealie.import_recipe_from_url(url)
        except Exception as e:
            error_msg = f"Error importing recipe from URL '{url}': {str(e)}"
            logger.error({"message": error_msg})
            logger.debug(
                {"message": "Error traceback", "traceback": traceback.format_exc()}
            )
            return format_error_response(error_msg)
