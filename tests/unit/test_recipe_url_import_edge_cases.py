"""Edge case tests for recipe URL import functionality."""

import json

import pytest
from fastmcp import Client

from tests.conftest import create_test_server


@pytest.mark.asyncio
async def test_import_recipe_with_very_long_url(test_env, httpx_mock):
    """Test handling of extremely long URLs."""
    mcp_server = create_test_server(httpx_mock)

    base_url = "https://example.com/recipes/very-long-recipe-name"
    long_params = "&".join([f"param{i}=value{i}" for i in range(50)])
    long_url = f"{base_url}?{long_params}"

    httpx_mock.add_response(
        method="POST",
        url="http://test.mealie.local/api/recipes/create/url",
        json="truncated-recipe-name",
        status_code=201,
    )

    httpx_mock.add_response(
        method="GET",
        url="http://test.mealie.local/api/recipes/truncated-recipe-name",
        json={
            "id": "long-url-recipe",
            "slug": "truncated-recipe-name",
            "name": "Recipe with Long URL",
            "orgURL": long_url,
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
            {"url": long_url}
        )

        response_text = result[0].text
        response_data = json.loads(response_text)

        assert response_data["slug"] == "truncated-recipe-name"
        assert len(response_data["orgURL"]) > 200


@pytest.mark.asyncio
async def test_import_recipe_with_authentication_required(test_env, httpx_mock):
    """Test handling when source site requires authentication."""
    mcp_server = create_test_server(httpx_mock)

    httpx_mock.add_response(
        method="POST",
        url="http://test.mealie.local/api/recipes/create/url",
        status_code=401,
        json={"detail": "Source site requires authentication"},
    )

    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "import_recipe_from_url",
            {"url": "https://premium-recipes.com/members-only/recipe"}
        )

        response_text = result[0].text
        response_data = json.loads(response_text)

        assert response_data["success"] is False
        assert "401" in response_data["error"] or "authentication" in response_data["error"].lower()


@pytest.mark.asyncio
async def test_import_recipe_with_rate_limiting(test_env, httpx_mock):
    """Test handling of rate limiting responses."""
    mcp_server = create_test_server(httpx_mock)

    httpx_mock.add_response(
        method="POST",
        url="http://test.mealie.local/api/recipes/create/url",
        status_code=429,
        json={"detail": "Rate limit exceeded. Please try again later."},
        headers={"Retry-After": "60"},
    )

    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "import_recipe_from_url",
            {"url": "https://popular-site.com/recipe"}
        )

        response_text = result[0].text
        response_data = json.loads(response_text)

        assert response_data["success"] is False
        assert "429" in response_data["error"] or "rate limit" in response_data["error"].lower()


@pytest.mark.asyncio
async def test_import_recipe_with_redirect_url(test_env, httpx_mock):
    """Test handling when URL redirects to actual recipe."""
    mcp_server = create_test_server(httpx_mock)

    httpx_mock.add_response(
        method="POST",
        url="http://test.mealie.local/api/recipes/create/url",
        json="final-recipe-location",
        status_code=201,
    )

    httpx_mock.add_response(
        method="GET",
        url="http://test.mealie.local/api/recipes/final-recipe-location",
        json={
            "id": "redirected-recipe",
            "slug": "final-recipe-location",
            "name": "Recipe After Redirect",
            "orgURL": "https://example.com/recipes/final-location",
            "description": "This recipe was imported from a redirected URL",
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
            {"url": "https://short.link/abc123"}
        )

        response_text = result[0].text
        response_data = json.loads(response_text)

        assert response_data["name"] == "Recipe After Redirect"
        assert "final-location" in response_data["orgURL"]


@pytest.mark.asyncio
async def test_import_recipe_with_non_recipe_url(test_env, httpx_mock):
    """Test handling when URL points to non-recipe content."""
    mcp_server = create_test_server(httpx_mock)

    httpx_mock.add_response(
        method="POST",
        url="http://test.mealie.local/api/recipes/create/url",
        status_code=422,
        json={"detail": "No recipe data found at the provided URL"},
    )

    async with Client(mcp_server) as client:
        result = await client.call_tool(
            "import_recipe_from_url",
            {"url": "https://example.com/not-a-recipe"}
        )

        response_text = result[0].text
        response_data = json.loads(response_text)

        assert response_data["success"] is False
        assert "422" in response_data["error"] or "no recipe" in response_data["error"].lower()


@pytest.mark.asyncio
async def test_import_recipe_with_partial_data(test_env, httpx_mock):
    """Test importing recipe where scraper only gets partial data."""
    mcp_server = create_test_server(httpx_mock)

    httpx_mock.add_response(
        method="POST",
        url="http://test.mealie.local/api/recipes/create/url",
        json="incomplete-recipe",
        status_code=201,
    )

    httpx_mock.add_response(
        method="GET",
        url="http://test.mealie.local/api/recipes/incomplete-recipe",
        json={
            "id": "partial-recipe",
            "slug": "incomplete-recipe",
            "name": "Partially Scraped Recipe",
            "orgURL": "https://difficult-site.com/recipe",
            "description": "Some data could not be extracted",
            "recipeIngredient": [
                {"note": "Some ingredients were found"},
                {"note": "But the list may be incomplete"},
            ],
            "recipeInstructions": [],
            "warnings": [
                "Could not extract cooking instructions",
                "Nutrition information unavailable",
                "Serving size could not be determined"
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
            {"url": "https://difficult-site.com/recipe"}
        )

        response_text = result[0].text
        response_data = json.loads(response_text)

        assert response_data["name"] == "Partially Scraped Recipe"
        assert len(response_data["recipeIngredient"]) == 2
        assert len(response_data["recipeInstructions"]) == 0
        assert "warnings" in response_data


@pytest.mark.asyncio
async def test_import_recipe_concurrent_requests(test_env, httpx_mock):
    """Test that concurrent imports of the same URL are handled."""
    mcp_server = create_test_server(httpx_mock)

    httpx_mock.add_response(
        method="POST",
        url="http://test.mealie.local/api/recipes/create/url",
        json="concurrent-recipe",
        status_code=201,
    )

    httpx_mock.add_response(
        method="GET",
        url="http://test.mealie.local/api/recipes/concurrent-recipe",
        json={
            "id": "first-import",
            "slug": "concurrent-recipe",
            "name": "Concurrent Import Recipe",
            "orgURL": "https://example.com/popular-recipe",
            "dateAdded": "2024-01-15T10:00:00Z",
            "dateUpdated": "2024-01-15T10:00:00Z",
            "userId": "user-123",
            "groupId": "group-123",
            "householdId": "household-123",
            "createdAt": "2024-01-15T10:00:00Z",
            "updatedAt": "2024-01-15T10:00:00Z",
        },
    )

    httpx_mock.add_response(
        method="POST",
        url="http://test.mealie.local/api/recipes/create/url",
        status_code=409,
        json={"detail": "Recipe import already in progress for this URL"},
    )

    async with Client(mcp_server) as client:
        result1 = await client.call_tool(
            "import_recipe_from_url",
            {"url": "https://example.com/popular-recipe"}
        )

        response1_data = json.loads(result1[0].text)
        assert response1_data["name"] == "Concurrent Import Recipe"

        result2 = await client.call_tool(
            "import_recipe_from_url",
            {"url": "https://example.com/popular-recipe"}
        )

        response2_data = json.loads(result2[0].text)
        assert response2_data["success"] is False
        assert "409" in response2_data["error"] or "in progress" in response2_data["error"].lower()