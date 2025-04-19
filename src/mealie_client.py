from typing import Any, Dict, List, Optional

import httpx


class MealieClient:
    def __init__(self, base_url: str, api_key: str):
        self._client = httpx.Client(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

    def get_foods(
        self,
        search: Optional[str] = None,
        order_by: Optional[str] = None,
        order_by_null_position: Optional[str] = None,
        order_direction: Optional[str] = "desc",
        query_filter: Optional[str] = None,
        pagination_seed: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Provides paginated list of foods

        Args:
            search: Search term to filter foods by name
            order_by: Field to order results by
            order_by_null_position: How to handle nulls in ordering ('first' or 'last')
            order_direction: Direction to order results ('asc' or 'desc')
            query_filter: Advanced query filter
            pagination_seed: Seed for consistent pagination
            page: Page number to retrieve
            per_page: Number of items per page

        Returns:
            JSON response containing food items and pagination information
        """
        params = {}

        if search is not None:
            params["search"] = search
        if order_by is not None:
            params["orderBy"] = order_by
        if order_by_null_position is not None:
            params["orderByNullPosition"] = order_by_null_position
        if order_direction is not None:
            params["orderDirection"] = order_direction
        if query_filter is not None:
            params["queryFilter"] = query_filter
        if pagination_seed is not None:
            params["paginationSeed"] = pagination_seed
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["perPage"] = per_page

        response = self._client.get("/api/foods", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    def get_recipes(
        self,
        search: Optional[str] = None,
        order_by: Optional[str] = None,
        order_by_null_position: Optional[str] = None,
        order_direction: Optional[str] = "desc",
        query_filter: Optional[str] = None,
        pagination_seed: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        tools: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Provides paginated list of recipes

        Args:
            search: Search term to filter recipes by name, description, etc.
            order_by: Field to order results by
            order_by_null_position: How to handle nulls in ordering ('first' or 'last')
            order_direction: Direction to order results ('asc' or 'desc')
            query_filter: Advanced query filter
            pagination_seed: Seed for consistent pagination
            page: Page number to retrieve
            per_page: Number of items per page
            categories: List of category slugs to filter by
            tags: List of tag slugs to filter by
            tools: List of tool slugs to filter by

        Returns:
            JSON response containing recipe items and pagination information
        """
        params = {}

        if search is not None:
            params["search"] = search
        if order_by is not None:
            params["orderBy"] = order_by
        if order_by_null_position is not None:
            params["orderByNullPosition"] = order_by_null_position
        if order_direction is not None:
            params["orderDirection"] = order_direction
        if query_filter is not None:
            params["queryFilter"] = query_filter
        if pagination_seed is not None:
            params["paginationSeed"] = pagination_seed
        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["perPage"] = per_page
        if categories is not None:
            params["categories"] = ",".join(categories)
        if tags is not None:
            params["tags"] = ",".join(tags)
        if tools is not None:
            params["tools"] = ",".join(tools)

        response = self._client.get("/api/recipes", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    def get_recipe(self, slug: str) -> Dict[str, Any]:
        """Retrieve a specific recipe by its slug

        Args:
            slug: The slug identifier of the recipe to retrieve

        Returns:
            JSON response containing all recipe details
        """
        response = self._client.get(f"/api/recipes/{slug}")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    def create_shopping_list(
        self, name: str, description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new shopping list

        Args:
            name: The name of the shopping list
            description: Optional description for the shopping list

        Returns:
            JSON response containing the created shopping list details
        """
        payload = {"name": name}

        if description is not None:
            payload["description"] = description

        response = self._client.post("/api/households/shopping/lists", json=payload)
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    def update_shopping_list(
        self,
        list_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing shopping list

        Args:
            list_id: The ID of the shopping list to update
            name: New name for the shopping list
            description: New description for the shopping list

        Returns:
            JSON response containing the updated shopping list details
        """
        payload = {"id": list_id}

        if name is not None:
            payload["name"] = name

        if description is not None:
            payload["description"] = description

        response = self._client.put(
            f"/api/households/shopping/lists/{list_id}", json=payload
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    def get_shopping_lists(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        pagination_seed: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Retrieve all shopping lists

        Args:
            page: Page number to retrieve
            per_page: Number of items per page
            pagination_seed: Seed for consistent pagination

        Returns:
            JSON response containing shopping list items and pagination information
        """
        params = {}

        if page is not None:
            params["page"] = page
        if per_page is not None:
            params["perPage"] = per_page
        if pagination_seed is not None:
            params["paginationSeed"] = pagination_seed

        response = self._client.get("/api/households/shopping/lists", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    def get_shopping_list(self, list_id: str) -> Dict[str, Any]:
        """Retrieve a specific shopping list by ID

        Args:
            list_id: The ID of the shopping list to retrieve

        Returns:
            JSON response containing the shopping list details
        """
        response = self._client.get(f"/api/households/shopping/lists/{list_id}")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")
