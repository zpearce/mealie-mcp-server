"""Consolidated unit tests for recipe update functionality."""

import json
import pytest
from fastmcp import Client


def get_minimal_recipe():
    """Get a minimal valid recipe for testing"""
    return {
        "id": "test-id",
        "userId": "user-123",
        "householdId": "household-123",
        "groupId": "group-123",
        "name": "Test Recipe",
        "slug": "test-recipe",
        "dateAdded": "2024-01-01T12:00:00Z",
        "dateUpdated": "2024-01-15T12:00:00Z",
        "createdAt": "2024-01-01T12:00:00Z",
        "updatedAt": "2024-01-15T12:00:00Z",
        "recipeIngredient": [],
        "recipeInstructions": []
    }


@pytest.mark.asyncio
async def test_update_recipe_replaces_ingredients_and_instructions(test_env, httpx_mock):
    """Test that update_recipe replaces ingredients and instructions while preserving other fields"""
    from tests.conftest import create_test_server

    mcp_server = create_test_server(httpx_mock)

    initial_recipe = get_minimal_recipe()
    initial_recipe.update({
        "description": "Original description",
        "rating": 4.5,
        "recipeCategory": ["italian"],
        "tags": ["easy"],
        "extras": {"custom": "data"}
    })

    httpx_mock.add_response(
        method="GET",
        url="http://test.mealie.local/api/recipes/test-recipe",
        json=initial_recipe
    )

    expected_update = initial_recipe.copy()
    expected_update["recipeIngredient"] = [
        {"note": "2 cups flour"},
        {"note": "1 cup water"}
    ]
    expected_update["recipeInstructions"] = [
        {"text": "Mix ingredients"},
        {"text": "Bake for 30 minutes"}
    ]

    httpx_mock.add_response(
        method="PUT",
        url="http://test.mealie.local/api/recipes/test-recipe",
        json=expected_update
    )

    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "update_recipe",
            {
                "slug": "test-recipe",
                "ingredients": ["2 cups flour", "1 cup water"],
                "instructions": ["Mix ingredients", "Bake for 30 minutes"]
            }
        )

    response_data = json.loads(result[0].text)

    assert len(response_data["recipeIngredient"]) == 2
    assert response_data["recipeIngredient"][0]["note"] == "2 cups flour"
    assert len(response_data["recipeInstructions"]) == 2
    assert response_data["recipeInstructions"][0]["text"] == "Mix ingredients"

    assert response_data["description"] == "Original description"
    assert response_data["rating"] == 4.5
    assert response_data["extras"]["custom"] == "data"


@pytest.mark.asyncio
async def test_update_recipe_handles_empty_lists(test_env, httpx_mock):
    """Test that empty ingredient/instruction lists work correctly"""
    from tests.conftest import create_test_server

    mcp_server = create_test_server(httpx_mock)

    initial_recipe = get_minimal_recipe()
    initial_recipe["recipeIngredient"] = [{"note": "old ingredient"}]
    initial_recipe["recipeInstructions"] = [{"text": "old instruction"}]

    httpx_mock.add_response(
        method="GET",
        url="http://test.mealie.local/api/recipes/test-recipe",
        json=initial_recipe
    )

    expected_update = initial_recipe.copy()
    expected_update["recipeIngredient"] = []
    expected_update["recipeInstructions"] = []

    httpx_mock.add_response(
        method="PUT",
        url="http://test.mealie.local/api/recipes/test-recipe",
        json=expected_update
    )

    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "update_recipe",
            {
                "slug": "test-recipe",
                "ingredients": [],
                "instructions": []
            }
        )

    response_data = json.loads(result[0].text)
    assert response_data["recipeIngredient"] == []
    assert response_data["recipeInstructions"] == []


@pytest.mark.asyncio
@pytest.mark.parametrize("field_name,field_value,api_field,expected_value", [
    ("tags", ["ww-points-5", "family-favorite"], "tags", ["ww-points-5", "family-favorite"]),
    ("categories", ["dinner", "italian"], "recipeCategory", ["dinner", "italian"]),
    ("extras", {"last_cooked": "2024-01-20", "ww_points": "7"}, "extras", {"last_cooked": "2024-01-20", "ww_points": "7"}),
    ("nutrition", {"calories": "350", "proteinContent": "25"}, "nutrition", {"calories": "350", "proteinContent": "25"}),
    ("tools", ["instant-pot", "mixer"], "tools", ["instant-pot", "mixer"]),
    ("settings", {"public": False, "showNutrition": True}, "settings", {"public": False, "showNutrition": True}),
    ("org_url", "https://example.com/recipe", "orgURL", "https://example.com/recipe"),
    ("description", "Updated description", "description", "Updated description"),
    ("recipe_servings", 8, "recipeServings", 8.0),
    ("recipe_yield", "8 servings", "recipeYield", "8 servings"),
    ("prep_time", "30", "prepTime", "30"),
    ("cook_time", "45", "cookTime", "45"),
    ("total_time", "75", "totalTime", "75"),
])
async def test_update_recipe_optional_fields(field_name, field_value, api_field, expected_value, test_env, httpx_mock):
    """Test updating various optional recipe fields"""
    from tests.conftest import create_test_server

    mcp_server = create_test_server(httpx_mock)

    initial_recipe = get_minimal_recipe()
    if isinstance(field_value, list):
        initial_recipe[api_field] = ["old-value"]
    elif isinstance(field_value, dict):
        initial_recipe[api_field] = {"old": "value"}
    elif isinstance(field_value, int):
        initial_recipe[api_field] = 99
    elif isinstance(field_value, float):
        initial_recipe[api_field] = 99.0
    else:
        initial_recipe[api_field] = "old-value"

    httpx_mock.add_response(
        method="GET",
        url="http://test.mealie.local/api/recipes/test-recipe",
        json=initial_recipe
    )

    expected_update = initial_recipe.copy()
    expected_update[api_field] = expected_value
    expected_update["recipeIngredient"] = [{"note": "ingredient"}]
    expected_update["recipeInstructions"] = [{"text": "instruction"}]

    httpx_mock.add_response(
        method="PUT",
        url="http://test.mealie.local/api/recipes/test-recipe",
        json=expected_update
    )

    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "update_recipe",
            {
                "slug": "test-recipe",
                "ingredients": ["ingredient"],
                "instructions": ["instruction"],
                field_name: field_value
            }
        )

    response_data = json.loads(result[0].text)

    if isinstance(expected_value, dict):
        assert response_data[api_field] == expected_value
    elif isinstance(expected_value, list):
        assert response_data[api_field] == expected_value
    else:
        assert response_data[api_field] == expected_value


@pytest.mark.asyncio
async def test_update_recipe_with_name(test_env, httpx_mock):
    """Test that the update_recipe tool supports updating the recipe name."""
    from tests.conftest import create_test_server

    mcp_server = create_test_server(httpx_mock)

    initial_recipe = get_minimal_recipe()
    initial_recipe["name"] = "Original Name"

    httpx_mock.add_response(
        method="GET",
        url="http://test.mealie.local/api/recipes/test-recipe",
        json=initial_recipe
    )

    expected_update = initial_recipe.copy()
    expected_update["name"] = "New Name"
    expected_update["recipeIngredient"] = [{"note": "ingredient"}]
    expected_update["recipeInstructions"] = [{"text": "instruction"}]

    httpx_mock.add_response(
        method="PUT",
        url="http://test.mealie.local/api/recipes/test-recipe",
        json=expected_update
    )

    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "update_recipe",
            {
                "slug": "test-recipe",
                "ingredients": ["ingredient"],
                "instructions": ["instruction"],
                "name": "New Name"
            }
        )

        response_data = json.loads(result[0].text)
        assert response_data["name"] == "New Name"


@pytest.mark.asyncio
async def test_update_recipe_preserves_all_fields(test_env, httpx_mock):
    """Test that all recipe fields are preserved during update - comprehensive test"""
    from tests.conftest import create_test_server

    mcp_server = create_test_server(httpx_mock)

    complex_recipe = get_minimal_recipe()
    complex_recipe.update({
        "description": "A complex recipe",
        "recipeServings": 6.0,
        "recipeYieldQuantity": 6,
        "recipeYield": "6 servings",
        "totalTime": "60",
        "prepTime": "20",
        "cookTime": "40",
        "recipeCategory": ["dinner", "italian"],
        "tags": ["easy", "vegetarian"],
        "rating": 4.8,
        "orgURL": "https://example.com/recipe",
        "tools": ["oven", "mixer"],
        "nutrition": {
            "calories": "300",
            "proteinContent": "15",
            "carbohydrateContent": "40",
            "fatContent": "10"
        },
        "settings": {
            "public": True,
            "showNutrition": True,
            "showAssets": False,
            "landscapeView": False,
            "disableComments": False,
            "disableAmount": False,
            "locked": False
        },
        "extras": {
            "field1": "value1",
            "field2": "value2"
        },
        "notes": ["Note 1"],
        "comments": ["Comment 1"]
    })

    httpx_mock.add_response(
        method="GET",
        url="http://test.mealie.local/api/recipes/test-recipe",
        json=complex_recipe
    )

    expected_update = complex_recipe.copy()
    expected_update["recipeIngredient"] = [{"note": "new ingredient"}]
    expected_update["recipeInstructions"] = [{"text": "new instruction"}]

    httpx_mock.add_response(
        method="PUT",
        url="http://test.mealie.local/api/recipes/test-recipe",
        json=expected_update
    )

    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "update_recipe",
            {
                "slug": "test-recipe",
                "ingredients": ["new ingredient"],
                "instructions": ["new instruction"]
            }
        )

    response_data = json.loads(result[0].text)

    assert response_data["description"] == "A complex recipe"
    assert response_data["recipeServings"] == 6.0
    assert response_data["totalTime"] == "60"
    assert response_data["recipeCategory"] == ["dinner", "italian"]
    assert response_data["tags"] == ["easy", "vegetarian"]
    assert response_data["rating"] == 4.8
    assert response_data["nutrition"]["calories"] == "300"
    assert response_data["settings"]["public"] is True
    assert response_data["extras"]["field1"] == "value1"
    assert response_data["extras"]["field2"] == "value2"
