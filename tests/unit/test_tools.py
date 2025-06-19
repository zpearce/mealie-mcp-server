"""Unit tests for MCP tool functions."""

import json

import pytest
from fastmcp import Client

from tests.conftest import create_test_server


@pytest.mark.asyncio
async def test_get_recipes_tool(test_env, httpx_mock):
    """Test the get_recipes tool returns recipe list."""
    # Create server after setting up initial mock
    mcp_server = create_test_server(httpx_mock)
    
    # Mock the recipe list API call
    httpx_mock.add_response(
        method="GET",
        url="http://test.mealie.local/api/recipes?orderDirection=desc&perPage=10",
        json={
            "page": 1,
            "per_page": 10,
            "total": 2,
            "total_pages": 1,
            "items": [
                {
                    "id": "recipe-1",
                    "slug": "chicken-parmesan",
                    "name": "Chicken Parmesan",
                    "description": "Classic Italian-American dish",
                },
                {
                    "id": "recipe-2", 
                    "slug": "spaghetti-carbonara",
                    "name": "Spaghetti Carbonara",
                    "description": "Traditional Roman pasta",
                },
            ],
        },
    )
    
    async with Client(mcp_server) as client:
        result = await client.call_tool("get_recipes", {"per_page": 10})
        
        response_text = result[0].text
        assert "Chicken Parmesan" in response_text
        assert "Spaghetti Carbonara" in response_text
        assert "chicken-parmesan" in response_text
        assert "spaghetti-carbonara" in response_text


@pytest.mark.asyncio
async def test_get_recipe_detailed(test_env, httpx_mock):
    """Test getting detailed recipe information."""
    # Create server after setting up initial mock
    mcp_server = create_test_server(httpx_mock)
    
    # Mock the recipe detail API call
    httpx_mock.add_response(
        url="http://test.mealie.local/api/recipes/chicken-parmesan",
        json={
            "id": "recipe-1",
            "slug": "chicken-parmesan",
            "name": "Chicken Parmesan",
            "description": "Classic Italian-American dish",
            "ingredients": [
                {"note": "2 chicken breasts"},
                {"note": "1 cup breadcrumbs"},
                {"note": "2 cups marinara sauce"},
                {"note": "1 cup mozzarella cheese"},
            ],
            "instructions": [
                {"text": "Bread the chicken"},
                {"text": "Fry until golden"},
                {"text": "Top with sauce and cheese"},
                {"text": "Bake until bubbly"},
            ],
            "nutrition": {
                "calories": 450,
                "protein": 35,
                "carbs": 25,
                "fat": 20,
            },
        },
    )
    
    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "get_recipe_detailed", 
            {"slug": "chicken-parmesan"}
        )
        
        response_text = result[0].text
        response_data = json.loads(response_text)
        
        assert response_data["name"] == "Chicken Parmesan"
        assert response_data["slug"] == "chicken-parmesan"
        assert len(response_data["ingredients"]) == 4
        assert len(response_data["instructions"]) == 4
        assert response_data["nutrition"]["calories"] == 450


@pytest.mark.asyncio
async def test_recipe_not_found_error(test_env, httpx_mock):
    """Test handling of 404 errors from Mealie API."""
    # Create server after setting up initial mock
    mcp_server = create_test_server(httpx_mock)
    
    # Mock 404 response
    httpx_mock.add_response(
        url="http://test.mealie.local/api/recipes/nonexistent",
        status_code=404,
        json={"detail": "Recipe not found"},
    )
    
    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "get_recipe_detailed",
            {"slug": "nonexistent"}
        )
        
        response_text = result[0].text
        response_data = json.loads(response_text)
        
        assert response_data["success"] is False
        assert "404" in response_data["error"]
        assert "not found" in response_data["error"].lower()


@pytest.mark.asyncio
async def test_get_recipes_with_search(test_env, httpx_mock):
    """Test recipe search with search parameter."""
    # Create server after setting up initial mock
    mcp_server = create_test_server(httpx_mock)
    
    # Mock search response - note the exact query string format
    httpx_mock.add_response(
        method="GET",
        url="http://test.mealie.local/api/recipes?orderDirection=desc&search=chicken&perPage=20",
        json={
            "items": [
                {
                    "id": "recipe-1",
                    "slug": "chicken-parmesan",
                    "name": "Chicken Parmesan",
                },
                {
                    "id": "recipe-3",
                    "slug": "chicken-tikka",
                    "name": "Chicken Tikka Masala",
                },
            ],
            "total": 2,
        },
    )
    
    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "get_recipes",
            {
                "search": "chicken",
                "per_page": 20,
            }
        )
        
        response_text = result[0].text
        assert "Chicken Parmesan" in response_text
        assert "Chicken Tikka Masala" in response_text


@pytest.mark.asyncio
async def test_create_recipe_with_details(test_env, httpx_mock):
    """Test creating a recipe with required details."""
    # Create server after setting up initial mock
    mcp_server = create_test_server(httpx_mock)
    
    # Mock recipe creation
    httpx_mock.add_response(
        method="POST",
        url="http://test.mealie.local/api/recipes",
        json={
            "id": "new-recipe-1",
            "slug": "test-recipe",
            "name": "Test Recipe",
        },
    )
    
    # Mock recipe retrieval (needed for update flow)
    httpx_mock.add_response(
        method="GET",
        url="http://test.mealie.local/api/recipes/test-recipe",
        json={
            "id": "new-recipe-1",
            "slug": "test-recipe",
            "name": "Test Recipe",
            "userId": "user-123",
            "householdId": "household-123",
            "groupId": "group-123",
            "dateAdded": "2024-01-01T00:00:00Z",
            "dateUpdated": "2024-01-01T00:00:00Z",
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-01T00:00:00Z",
            "recipeIngredient": [],
            "recipeInstructions": [],
        },
    )
    
    # Mock recipe update
    httpx_mock.add_response(
        method="PUT",
        url="http://test.mealie.local/api/recipes/test-recipe",
        json={
            "id": "new-recipe-1",
            "slug": "test-recipe",
            "name": "Test Recipe",
            "userId": "user-123",
            "householdId": "household-123",
            "groupId": "group-123",
            "dateAdded": "2024-01-01T00:00:00Z",
            "dateUpdated": "2024-01-01T00:00:00Z",
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-01T00:00:00Z",
            "recipeIngredient": [
                {"note": "2 cups flour"},
                {"note": "1 cup water"},
            ],
            "recipeInstructions": [
                {"text": "Mix ingredients"},
                {"text": "Bake at 350F"},
            ],
        },
    )
    
    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "create_recipe",
            {
                "name": "Test Recipe",
                "ingredients": ["2 cups flour", "1 cup water"],
                "instructions": ["Mix ingredients", "Bake at 350F"],
            }
        )
        
        response_text = result[0].text
        response_data = json.loads(response_text)
        
        assert response_data["name"] == "Test Recipe"
        assert response_data["slug"] == "test-recipe"
        assert len(response_data["recipeIngredient"]) == 2
        assert len(response_data["recipeInstructions"]) == 2