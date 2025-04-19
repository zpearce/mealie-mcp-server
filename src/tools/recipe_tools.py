import logging
import traceback
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from mealie import MealieFetcher
from models.recipe import RecipeData
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

        Important Notes:
            - For best results, omit fields you don't want to change rather than providing empty values
            - For recipe ingredients, the default values are isFood=True and disableAmount=False
            - When providing empty lists (like tags or categories), use [] instead of null/None
            - Use string values for times (e.g., "15 minutes" instead of numeric values)
            - Put ingredient details (quantity, unit, food) into the note field for simplicity
            - Examples below are truncated for readability; a full recipe may have many more ingredients and instructions

        Example of updating a complete recipe with full details:
            ```json
            {
              "slug": "hot-cross-buns-recipe",
              "recipe_data": {
                "name": "Hot Cross Buns recipe",
                "description": "Fluffy, perfectly spiced homemade Hot Cross Buns! Watch video to see the dough before and after kneading, and how I roll the balls to get nice smooth golden tops. Also, see below for the NO KNEAD version!",
                "recipeServings": 12.0,
                "recipeYieldQuantity": 0.0,
                "recipeYield": "",
                "totalTime": "30 minutes",
                "prepTime": "15 minutes",
                "cookTime": "15 minutes",
                "performTime": null,
                "recipeCategory": [],
                "tags": [],
                "tools": [],
                "rating": null,
                "orgURL": "https://www.recipetineats.com/hot-cross-buns-recipe/",
                "nutrition": {
                  "calories": "217",
                  "carbohydrateContent": null,
                  "cholesterolContent": null,
                  "fatContent": null,
                  "fiberContent": null,
                  "proteinContent": null,
                  "saturatedFatContent": null,
                  "sodiumContent": null,
                  "sugarContent": null,
                  "transFatContent": null,
                  "unsaturatedFatContent": null
                },
                "recipeIngredient": [
                  {
                    "quantity": 1.0,
                    "unit": null,
                    "food": null,
                    "note": "3 teaspoons instant or rapid rise yeast (9 grams) (, Note 1, CHECK still active!)",
                    "isFood": false,
                    "disableAmount": true
                  }
                  // ... (other ingredients)
                ],
                "recipeInstructions": [
                  {
                    "title": "",
                    "summary": "",
                    "text": "Mix dry - Place flour, yeast, sugar, all spice, cinnamon, and salt in a large bowl. Briefly mix with stand mixer fitted with a dough hook."
                  }
                  // ... (other instructions)
                ],
                "settings": {
                  "public": false,
                  "showNutrition": false,
                  "showAssets": false,
                  "landscapeView": false,
                  "disableComments": false,
                  "disableAmount": false,
                  "locked": false
                }
              }
            }
            ```
        """
        try:
            logger.info({"message": "Updating recipe", "slug": slug})

            # Use Pydantic model for validation
            try:
                # Parse the recipe data through our Pydantic model
                validated_data = RecipeData(**recipe_data)
                # Convert back to dict for the API call
                recipe_data_dict = validated_data.model_dump(exclude_none=True)
                logger.debug(
                    {"message": "Validated recipe data", "data": recipe_data_dict}
                )

                # Make the API call with the validated data
                return mealie.update_recipe(slug=slug, recipe_data=recipe_data_dict)
            except Exception as validation_error:
                # Log the validation error details
                logger.error(
                    {"message": "Data validation error", "error": str(validation_error)}
                )
                logger.debug(
                    {
                        "message": "Original data that failed validation",
                        "data": recipe_data,
                    }
                )
                raise ValueError(f"Invalid recipe data format: {str(validation_error)}")
        except Exception as e:
            error_msg = f"Error updating recipe with slug '{slug}': {str(e)}"
            logger.error({"message": error_msg})
            logger.debug(
                {"message": "Error traceback", "traceback": traceback.format_exc()}
            )
            return format_error_response(error_msg)

    @mcp.tool()
    def create_recipe(name: str, recipe_data: Optional[Dict[str, Any]] = None) -> str:
        """Create a new recipe with optional detailed information.

        This tool combines the create and update recipe operations to allow you to create a recipe
        with more details than just a name. It first creates a basic recipe with the provided name,
        then optionally updates it with additional details.

        Args:
            name: The name of the new recipe to create.
            recipe_data: Optional detailed recipe data to include. Can contain the same fields as update_recipe.
                      If provided, this will be used to update the recipe immediately after creation.

        Returns:
            str: The new recipe details, including the generated slug for future reference.

        Important Notes:
            - For best results, omit fields you don't want to set rather than providing empty values
            - For recipe ingredients, the default values are isFood=True and disableAmount=False
            - When providing empty lists (like tags or categories), use [] instead of null/None
            - Use string values for times (e.g., "15 minutes" instead of numeric values)
            - Put ingredient details (quantity, unit, food) into the note field for simplicity

        Example of creating a recipe with just a name:
            ```json
            {
              "name": "Chocolate Chip Cookies"
            }
            ```

        Example of creating a recipe with additional details:
            ```json
            {
              "name": "Chocolate Chip Cookies",
              "recipe_data": {
                "name": "Chocolate Chip Cookies",
                "description": "Classic homemade chocolate chip cookies that are soft and chewy.",
                "recipeServings": 24.0,
                "recipeYieldQuantity": 0.0,
                "recipeYield": "24 cookies",
                "totalTime": "25 minutes",
                "prepTime": "15 minutes",
                "cookTime": "10 minutes",
                "performTime": null,
                "recipeCategory": [],
                "tags": [],
                "tools": [],
                "rating": null,
                "orgURL": "",
                "nutrition": {
                  "calories": "",
                  "carbohydrateContent": null,
                  "cholesterolContent": null,
                  "fatContent": null,
                  "fiberContent": null,
                  "proteinContent": null,
                  "saturatedFatContent": null,
                  "sodiumContent": null,
                  "sugarContent": null,
                  "transFatContent": null,
                  "unsaturatedFatContent": null
                },
                "recipeIngredient": [
                  {
                    "quantity": null,
                    "unit": null,
                    "food": null,
                    "note": "2.25 cups all-purpose flour",
                    "isFood": false,
                    "disableAmount": true
                  },
                  {
                    "quantity": null,
                    "unit": null,
                    "food": null,
                    "note": "1 tsp baking soda",
                    "isFood": false,
                    "disableAmount": true
                  }
                  // ... (other ingredients)
                ],
                "recipeInstructions": [
                  {
                    "title": "",
                    "summary": "",
                    "text": "Preheat oven to 375°F (190°C)."
                  },
                  {
                    "title": "",
                    "summary": "",
                    "text": "In a small bowl, mix flour, baking soda, and salt."
                  }
                  // ... (other instructions)
                ],
                "settings": {
                  "public": false,
                  "showNutrition": false,
                  "showAssets": false,
                  "landscapeView": false,
                  "disableComments": false,
                  "disableAmount": false,
                  "locked": false
                }
              }
            }
            ```
        """
        try:
            logger.info({"message": "Creating new recipe", "name": name})
            # First create the basic recipe
            create_result = mealie.create_recipe(name=name)

            # If we have additional recipe data, update the recipe with those details
            if recipe_data:
                slug = create_result
                if not slug:
                    return format_error_response(
                        "Failed to get slug from created recipe"
                    )

                logger.info({"message": "Updating newly created recipe", "slug": slug})

                # Use Pydantic model for validation
                try:
                    # Parse the recipe data through our Pydantic model
                    validated_data = RecipeData(**recipe_data)
                    # Convert back to dict for the API call - using model_dump instead of dict
                    recipe_data_dict = validated_data.model_dump(exclude_none=True)
                    logger.debug(
                        {"message": "Validated recipe data", "data": recipe_data_dict}
                    )

                    # Make the API call with the validated data
                    return mealie.update_recipe(slug=slug, recipe_data=recipe_data_dict)
                except Exception as validation_error:
                    # Log the validation error details
                    logger.error(
                        {
                            "message": "Data validation error",
                            "error": str(validation_error),
                        }
                    )
                    logger.debug(
                        {
                            "message": "Original data that failed validation",
                            "data": recipe_data,
                        }
                    )
                    raise ValueError(
                        f"Invalid recipe data format: {str(validation_error)}"
                    )

            return create_result

        except Exception as e:
            error_msg = f"Error creating recipe with name '{name}': {str(e)}"
            logger.error({"message": error_msg})
            logger.debug(
                {"message": "Error traceback", "traceback": traceback.format_exc()}
            )
            return format_error_response(error_msg)
