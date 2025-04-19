import logging
import traceback
from typing import Any, Dict, List, Optional

import httpx
from httpx import ConnectError, HTTPStatusError, ReadTimeout

logger = logging.getLogger("mealie-mcp.client")


class MealieApiError(Exception):
    """Custom exception for Mealie API errors with status code and response details."""

    def __init__(self, status_code: int, message: str, response_text: str = None):
        self.status_code = status_code
        self.message = message
        self.response_text = response_text
        super().__init__(f"{message} (Status Code: {status_code})")


class MealieClient:
    def __init__(self, base_url: str, api_key: str):
        if not base_url:
            raise ValueError("Base URL cannot be empty")
        if not api_key:
            raise ValueError("API key cannot be empty")

        logger.debug(f"Initializing MealieClient with base URL: {base_url}")
        try:
            self._client = httpx.Client(
                base_url=base_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,  # Set a reasonable timeout for requests
            )
            # Test connection
            logger.debug("Testing connection to Mealie API")
            self._client.get("/api/app/about")
            logger.info("Successfully connected to Mealie API")
        except ConnectError as e:
            error_msg = f"Failed to connect to Mealie API at {base_url}: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            raise ConnectionError(error_msg) from e
        except Exception as e:
            error_msg = f"Error initializing Mealie client: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            raise

    def _handle_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Common request handler with error handling for all API calls."""
        try:
            logger.debug(f"Making {method} request to {url}")

            if "params" in kwargs:
                logger.debug(f"Request parameters: {kwargs['params']}")
            if "json" in kwargs:
                logger.debug(f"Request payload: {kwargs['json']}")

            response = self._client.request(method, url, **kwargs)
            response.raise_for_status()  # Raise an exception for 4XX/5XX responses

            logger.debug(f"Request successful: {response.status_code}")
            return response.json()

        except HTTPStatusError as e:
            status_code = e.response.status_code
            error_detail = f"HTTP Error {status_code}"

            # Try to parse error details from response
            try:
                error_json = e.response.json()
                if isinstance(error_json, dict) and "detail" in error_json:
                    error_detail = error_json["detail"]
            except Exception:
                error_detail = e.response.text

            error_msg = f"API error for {method} {url}: {error_detail}"
            logger.error(error_msg)
            raise MealieApiError(status_code, error_msg, e.response.text) from e

        except ReadTimeout:
            error_msg = f"Request timeout for {method} {url}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            raise TimeoutError(error_msg)

        except ConnectError as e:
            error_msg = f"Connection error for {method} {url}: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            raise ConnectionError(error_msg) from e

        except Exception as e:
            error_msg = f"Unexpected error for {method} {url}: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            raise

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

        logger.info(f"Retrieving foods with parameters: {params}")
        return self._handle_request("GET", "/api/foods", params=params)

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

        logger.info(f"Retrieving recipes with parameters: {params}")
        return self._handle_request("GET", "/api/recipes", params=params)

    def get_recipe(self, slug: str) -> Dict[str, Any]:
        """Retrieve a specific recipe by its slug

        Args:
            slug: The slug identifier of the recipe to retrieve

        Returns:
            JSON response containing all recipe details
        """
        if not slug:
            raise ValueError("Recipe slug cannot be empty")

        logger.info(f"Retrieving recipe with slug: {slug}")
        return self._handle_request("GET", f"/api/recipes/{slug}")

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
        if not name:
            raise ValueError("Shopping list name cannot be empty")

        payload = {"name": name}

        if description is not None:
            payload["description"] = description

        logger.info(f"Creating shopping list with name: {name}")
        return self._handle_request(
            "POST", "/api/households/shopping/lists", json=payload
        )

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
        if not list_id:
            raise ValueError("Shopping list ID cannot be empty")

        if name is None and description is None:
            raise ValueError("At least one of name or description must be provided")

        payload = {"id": list_id}

        if name is not None:
            payload["name"] = name

        if description is not None:
            payload["description"] = description

        logger.info(f"Updating shopping list {list_id}")
        return self._handle_request(
            "PUT", f"/api/households/shopping/lists/{list_id}", json=payload
        )

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

        logger.info(f"Retrieving shopping lists with parameters: {params}")
        return self._handle_request(
            "GET", "/api/households/shopping/lists", params=params
        )

    def get_shopping_list(self, list_id: str) -> Dict[str, Any]:
        """Retrieve a specific shopping list by ID

        Args:
            list_id: The ID of the shopping list to retrieve

        Returns:
            JSON response containing the shopping list details
        """
        if not list_id:
            raise ValueError("Shopping list ID cannot be empty")

        logger.info(f"Retrieving shopping list with ID: {list_id}")
        return self._handle_request("GET", f"/api/households/shopping/lists/{list_id}")
