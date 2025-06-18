"""Unit tests for recipe URL import functionality."""

import json

import pytest
from fastmcp import Client

from tests.conftest import create_test_server


@pytest.mark.asyncio
async def test_import_recipe_from_url_success(test_env, httpx_mock):
    """Test successful recipe import from URL."""
    mcp_server = create_test_server(httpx_mock)

    httpx_mock.add_response(
        method="POST",
        url="http://test.mealie.local/api/recipes/create/url",
        json="chocolate-chip-cookies",
        status_code=201,
    )

    httpx_mock.add_response(
        method="GET",
        url="http://test.mealie.local/api/recipes/chocolate-chip-cookies",
        json={
            "id": "imported-recipe-1",
            "slug": "chocolate-chip-cookies",
            "name": "Best Chocolate Chip Cookies",
            "description": "Crispy on the outside, chewy on the inside",
            "orgURL": "https://example.com/chocolate-chip-cookies",
            "recipeIngredient": [
                {"note": "2 1/4 cups all-purpose flour"},
                {"note": "1 tsp baking soda"},
                {"note": "1 tsp salt"},
                {"note": "1 cup butter, softened"},
                {"note": "3/4 cup granulated sugar"},
                {"note": "3/4 cup packed brown sugar"},
                {"note": "2 large eggs"},
                {"note": "2 tsp vanilla extract"},
                {"note": "2 cups chocolate chips"},
            ],
            "recipeInstructions": [
                {"text": "Preheat oven to 375°F"},
                {"text": "Mix flour, baking soda and salt in bowl"},
                {"text": "Beat butter and sugars until creamy"},
                {"text": "Add eggs and vanilla, mix well"},
                {"text": "Gradually beat in flour mixture"},
                {"text": "Stir in chocolate chips"},
                {"text": "Drop by rounded tablespoons onto baking sheets"},
                {"text": "Bake 9-11 minutes or until golden brown"},
            ],
            "totalTime": 30,
            "prepTime": 15,
            "cookTime": 15,
            "recipeServings": 48,
            "recipeYield": "48 cookies",
            "nutrition": {
                "calories": "110",
                "fatContent": "5g",
                "carbohydrateContent": "15g",
                "proteinContent": "1g",
            },
            "dateAdded": "2024-01-15T10:00:00Z",
            "dateUpdated": "2024-01-15T10:00:00Z",
            "userId": "user-123",
            "groupId": "group-123",
            "householdId": "household-123",
            "createdAt": "2024-01-15T10:00:00Z",
            "updatedAt": "2024-01-15T10:00:00Z",
        },
    )

    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "import_recipe_from_url",
            {"url": "https://example.com/chocolate-chip-cookies"}
        )

        response_text = result[0].text
        response_data = json.loads(response_text)

        assert response_data["name"] == "Best Chocolate Chip Cookies"
        assert response_data["slug"] == "chocolate-chip-cookies"
        assert response_data["orgURL"] == "https://example.com/chocolate-chip-cookies"
        assert len(response_data["recipeIngredient"]) == 9
        assert len(response_data["recipeInstructions"]) == 8
        assert response_data["totalTime"] == 30
        assert response_data["nutrition"]["calories"] == "110"


@pytest.mark.asyncio
async def test_import_recipe_from_url_with_minimal_data(test_env, httpx_mock):
    """Test importing a recipe that returns minimal data from scraping."""
    mcp_server = create_test_server(httpx_mock)

    httpx_mock.add_response(
        method="POST",
        url="http://test.mealie.local/api/recipes/create/url",
        json="simple-pasta",
        status_code=201,
    )

    httpx_mock.add_response(
        method="GET",
        url="http://test.mealie.local/api/recipes/simple-pasta",
        json={
            "id": "minimal-recipe-1",
            "slug": "simple-pasta",
            "name": "Simple Pasta",
            "description": "",
            "orgURL": "https://example.com/simple-pasta",
            "recipeIngredient": [],
            "recipeInstructions": [],
            "dateAdded": "2024-01-15T10:00:00Z",
            "dateUpdated": "2024-01-15T10:00:00Z",
            "userId": "user-123",
            "groupId": "group-123",
            "householdId": "household-123",
            "createdAt": "2024-01-15T10:00:00Z",
            "updatedAt": "2024-01-15T10:00:00Z",
        },
    )

    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "import_recipe_from_url",
            {"url": "https://example.com/simple-pasta"}
        )

        response_text = result[0].text
        response_data = json.loads(response_text)

        assert response_data["name"] == "Simple Pasta"
        assert response_data["slug"] == "simple-pasta"
        assert response_data["recipeIngredient"] == []
        assert response_data["recipeInstructions"] == []


@pytest.mark.asyncio
async def test_import_recipe_from_invalid_url(test_env, httpx_mock):
    """Test handling of invalid URL format."""
    mcp_server = create_test_server(httpx_mock)

    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "import_recipe_from_url",
            {"url": "not-a-valid-url"}
        )

        response_text = result[0].text
        response_data = json.loads(response_text)

        assert response_data["success"] is False
        assert "invalid url" in response_data["error"].lower()


@pytest.mark.asyncio
async def test_import_recipe_from_url_network_error(test_env, httpx_mock):
    """Test handling of network errors during import."""
    mcp_server = create_test_server(httpx_mock)

    httpx_mock.add_response(
        method="POST",
        url="http://test.mealie.local/api/recipes/create/url",
        status_code=500,
        json={"detail": "Internal server error while fetching recipe"},
    )

    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "import_recipe_from_url",
            {"url": "https://example.com/recipe"}
        )

        response_text = result[0].text
        response_data = json.loads(response_text)

        assert response_data["success"] is False
        assert "500" in response_data["error"]


@pytest.mark.asyncio
async def test_import_recipe_from_url_unsupported_site(test_env, httpx_mock):
    """Test handling when Mealie can't scrape the provided URL."""
    mcp_server = create_test_server(httpx_mock)

    httpx_mock.add_response(
        method="POST",
        url="http://test.mealie.local/api/recipes/create/url",
        status_code=400,
        json={"detail": "Unable to scrape recipe from the provided URL"},
    )

    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "import_recipe_from_url",
            {"url": "https://unsupported-site.com/recipe"}
        )

        response_text = result[0].text
        response_data = json.loads(response_text)

        assert response_data["success"] is False
        assert "400" in response_data["error"]
        assert "unable to scrape" in response_data["error"].lower()


@pytest.mark.asyncio
async def test_import_recipe_from_url_timeout(test_env, httpx_mock):
    """Test handling of timeout during recipe import."""
    mcp_server = create_test_server(httpx_mock)

    httpx_mock.add_response(
        method="POST",
        url="http://test.mealie.local/api/recipes/create/url",
        status_code=504,
        json={"detail": "Gateway timeout while fetching recipe"},
    )

    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "import_recipe_from_url",
            {"url": "https://slow-site.com/recipe"}
        )

        response_text = result[0].text
        response_data = json.loads(response_text)

        assert response_data["success"] is False
        assert "504" in response_data["error"] or "timeout" in response_data["error"].lower()


@pytest.mark.asyncio
async def test_import_recipe_from_url_duplicate(test_env, httpx_mock):
    """Test handling when importing a recipe that already exists."""
    mcp_server = create_test_server(httpx_mock)

    httpx_mock.add_response(
        method="POST",
        url="http://test.mealie.local/api/recipes/create/url",
        status_code=409,
        json={"detail": "Recipe already exists with slug: chocolate-chip-cookies"},
    )

    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "import_recipe_from_url",
            {"url": "https://example.com/chocolate-chip-cookies"}
        )

        response_text = result[0].text
        response_data = json.loads(response_text)

        assert response_data["success"] is False
        assert "409" in response_data["error"] or "already exists" in response_data["error"].lower()


@pytest.mark.asyncio
async def test_import_recipe_with_special_characters(test_env, httpx_mock):
    """Test importing a recipe with special characters in name and content."""
    mcp_server = create_test_server(httpx_mock)

    httpx_mock.add_response(
        method="POST",
        url="http://test.mealie.local/api/recipes/create/url",
        json="grandmas-secret-recipe",
        status_code=201,
    )

    httpx_mock.add_response(
        method="GET",
        url="http://test.mealie.local/api/recipes/grandmas-secret-recipe",
        json={
            "id": "special-recipe-1",
            "slug": "grandmas-secret-recipe",
            "name": "Grandma's Secret Recipe™ - The Best!",
            "description": "A recipe with émojis 🍪 and spëcial characters",
            "orgURL": "https://example.com/grandmas-recipe",
            "recipeIngredient": [
                {"note": "1½ cups flour"},
                {"note": "¾ tsp salt"},
                {"note": "Pinch of love ❤️"},
            ],
            "recipeInstructions": [
                {"text": "Mix at 350°F (not 350°C!)"},
                {"text": "Stir counter-clockwise × 3"},
            ],
            "dateAdded": "2024-01-15T10:00:00Z",
            "dateUpdated": "2024-01-15T10:00:00Z",
            "userId": "user-123",
            "groupId": "group-123",
            "householdId": "household-123",
            "createdAt": "2024-01-15T10:00:00Z",
            "updatedAt": "2024-01-15T10:00:00Z",
        },
    )

    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "import_recipe_from_url",
            {"url": "https://example.com/grandmas-recipe"}
        )

        response_text = result[0].text
        response_data = json.loads(response_text)

        assert "Grandma's Secret Recipe™" in response_data["name"]
        assert "émojis 🍪" in response_data["description"]
        assert "1½ cups flour" in response_data["recipeIngredient"][0]["note"]
        assert "350°F" in response_data["recipeInstructions"][0]["text"]


@pytest.mark.asyncio
async def test_import_recipe_empty_url(test_env, httpx_mock):
    """Test handling of empty URL parameter."""
    mcp_server = create_test_server(httpx_mock)

    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "import_recipe_from_url",
            {"url": ""}
        )

        response_text = result[0].text
        response_data = json.loads(response_text)

        assert response_data["success"] is False
        assert "url" in response_data["error"].lower()


@pytest.mark.asyncio
async def test_import_recipe_missing_url_parameter(test_env, httpx_mock):
    """Test handling when URL parameter is missing."""
    mcp_server = create_test_server(httpx_mock)

    async with Client(mcp_server) as client:
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("import_recipe_from_url", {})

        assert "url" in str(exc_info.value).lower()
