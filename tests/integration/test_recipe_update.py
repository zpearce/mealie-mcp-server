"""Consolidated integration tests for recipe update functionality against real Mealie instance."""

import pytest
from tests.integration.test_mealie_container import (
    mealie_container,
    mealie_api_client,
)


class TestRecipeUpdateIntegration:
    """Test recipe update functionality against a real Mealie instance."""

    @pytest.mark.integration
    def test_update_recipe_basic_fields(self, mealie_api_client):
        """Test updating basic recipe fields in a real Mealie instance."""
        recipe_slug = mealie_api_client.create_recipe("Integration Test Recipe")

        recipe = mealie_api_client.get_recipe(recipe_slug)

        recipe.update({
            "description": "A simple test recipe for integration testing",
            "recipeServings": 6.0,
            "prepTime": 10,
            "cookTime": 20,
            "totalTime": 30,
            "recipeIngredient": [
                {"note": "2 cups flour"},
                {"note": "1 cup sugar"},
                {"note": "3 eggs"}
            ],
            "recipeInstructions": [
                {"text": "Mix dry ingredients"},
                {"text": "Add eggs and mix well"},
                {"text": "Bake at 350F for 20 minutes"}
            ]
        })

        updated_recipe = mealie_api_client.update_recipe(recipe_slug, recipe)

        assert updated_recipe["description"] == "A simple test recipe for integration testing"
        assert updated_recipe["recipeServings"] == 6.0
        assert updated_recipe["prepTime"] == "10"
        assert updated_recipe["cookTime"] == "20"
        assert updated_recipe["totalTime"] == "30"
        assert len(updated_recipe["recipeIngredient"]) == 3
        assert len(updated_recipe["recipeInstructions"]) == 3

    @pytest.mark.integration
    @pytest.mark.skip("Tags and categories require existing entities - will implement after tag/category management")
    def test_update_recipe_tags_and_categories(self, mealie_api_client):
        """Test updating recipe tags and categories."""
        recipe_slug = mealie_api_client.create_recipe("Tag Test Recipe")

        recipe = mealie_api_client.get_recipe(recipe_slug)

        recipe.update({
            "tags": ["ww-points-5", "family-favorite", "quick-meal"],
            "recipeCategory": ["dinner", "comfort-food"],
            "recipeIngredient": [{"note": "test ingredient"}],
            "recipeInstructions": [{"text": "test instruction"}]
        })

        updated_recipe = mealie_api_client.update_recipe(recipe_slug, recipe)

        assert len(updated_recipe["tags"]) == 3
        assert "ww-points-5" in updated_recipe["tags"]
        assert "family-favorite" in updated_recipe["tags"]
        assert len(updated_recipe["recipeCategory"]) == 2
        assert "dinner" in updated_recipe["recipeCategory"]

    @pytest.mark.integration
    def test_update_recipe_extras_field(self, mealie_api_client):
        """Test updating the extras field for custom metadata."""
        recipe_slug = mealie_api_client.create_recipe("Extras Test Recipe")

        recipe = mealie_api_client.get_recipe(recipe_slug)

        extras_data = {
            "last_cooked": "2024-01-20",
            "cooked_count": "5",
            "ww_points": "7"
        }

        recipe.update({
            "extras": extras_data,
            "recipeIngredient": [{"note": "test"}],
            "recipeInstructions": [{"text": "test"}]
        })

        updated_recipe = mealie_api_client.update_recipe(recipe_slug, recipe)

        assert updated_recipe["extras"]["last_cooked"] == "2024-01-20"
        assert updated_recipe["extras"]["cooked_count"] == "5"
        assert updated_recipe["extras"]["ww_points"] == "7"

    @pytest.mark.integration
    def test_update_recipe_nutrition(self, mealie_api_client):
        """Test updating nutrition information."""
        recipe_slug = mealie_api_client.create_recipe("Nutrition Test Recipe")

        recipe = mealie_api_client.get_recipe(recipe_slug)

        recipe.update({
            "nutrition": {
                "calories": "350",
                "proteinContent": "25",
                "carbohydrateContent": "40",
                "fatContent": "12",
                "fiberContent": "5",
                "sodiumContent": "450"
            },
            "recipeIngredient": [{"note": "test"}],
            "recipeInstructions": [{"text": "test"}]
        })

        updated_recipe = mealie_api_client.update_recipe(recipe_slug, recipe)

        assert updated_recipe["nutrition"]["calories"] == "350"
        assert updated_recipe["nutrition"]["proteinContent"] == "25"

    @pytest.mark.integration
    def test_update_nonexistent_recipe(self, mealie_api_client):
        """Test error handling when updating non-existent recipe."""
        with pytest.raises(Exception) as exc_info:
            fake_recipe = {
                "name": "Fake",
                "recipeIngredient": [],
                "recipeInstructions": []
            }
            mealie_api_client.update_recipe("nonexistent-recipe-xyz", fake_recipe)

        assert "404" in str(exc_info.value)

    @pytest.mark.integration
    @pytest.mark.skip("Tags require existing entities - will implement after tag/category management")
    def test_recipe_import_and_update_workflow(self, mealie_api_client):
        """Test complete workflow: import recipe, then update it."""
        try:
            result = mealie_api_client.import_recipe_from_url(
                "https://www.allrecipes.com/recipe/10813/best-chocolate-chip-cookies/"
            )
            recipe_slug = result["slug"]

            recipe = mealie_api_client.get_recipe(recipe_slug)

            recipe.update({
                "tags": ["dessert", "cookies", "family-favorite"],
                "extras": {
                    "last_made": "2024-01-10",
                    "occasions": ["birthday", "holiday"],
                    "kid_approved": True
                }
            })

            updated = mealie_api_client.update_recipe(recipe_slug, recipe)

            assert "dessert" in updated["tags"]
            assert updated["extras"]["kid_approved"] is True

            assert len(updated["recipeIngredient"]) > 0
            assert len(updated["recipeInstructions"]) > 0

        except Exception as e:
            if "400" in str(e) or "422" in str(e):
                pytest.skip(f"Mealie couldn't parse the test URL: {e}")
            else:
                raise
