import logging
from typing import Any, Dict, List, Optional

from mealie.client import MealieClient
from param_builder import ParamBuilder

logger = logging.getLogger("mealie-mcp")


class MealplanMixin(MealieClient):
    """Mixin class for mealplan API interactions."""

    def get_all_mealplans(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get all meal plans, optionally filtered by date range.

        Args:
            start_date: Optional ISO format date string (YYYY-MM-DD) for start date filter
            end_date: Optional ISO format date string (YYYY-MM-DD) for end date filter
            page: Optional page number for pagination
            per_page: Optional number of items per page

        Returns:
            Dict containing meal plans and pagination information
        """
        params = ParamBuilder()
        if start_date is not None:
            params.add("start_date", start_date)
        if end_date is not None:
            params.add("end_date", end_date)
        if page is not None:
            params.add("page", page)
        if per_page is not None:
            params.add("per_page", per_page)

        return self._handle_request(
            "GET", "/api/households/mealplans", params=params.build()
        )

    def get_mealplan(self, item_id: int) -> Dict[str, Any]:
        """
        Get a specific meal plan entry by ID.

        Args:
            item_id: The ID of the meal plan entry

        Returns:
            Dict containing meal plan entry details
        """
        return self._handle_request(
            "GET", f"/api/households/mealplans/{item_id}"
        )

    def create_mealplan(self, mealplan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new meal plan entry.

        Args:
            mealplan_data: Dictionary containing meal plan entry details with the following fields:
                - date: Required. ISO format date string (YYYY-MM-DD)
                - entryType: Optional. One of 'breakfast', 'lunch', 'dinner', 'side'
                - title: Optional. Title for the meal
                - text: Optional. Text description 
                - recipeId: Optional. UUID of a recipe if this entry is linked to a recipe

        Returns:
            Dict containing the created meal plan entry
        """
        return self._handle_request(
            "POST", "/api/households/mealplans", json=mealplan_data
        )

    def update_mealplan(
        self, item_id: int, mealplan_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing meal plan entry.

        Args:
            item_id: The ID of the meal plan entry to update
            mealplan_data: Dictionary containing meal plan entry fields to update

        Returns:
            Dict containing the updated meal plan entry
        """
        return self._handle_request(
            "PUT", f"/api/households/mealplans/{item_id}", json=mealplan_data
        )

    def get_todays_meals(self) -> List[Dict[str, Any]]:
        """
        Get all meal plan entries for today.

        Returns:
            List of meal plan entries for the current day
        """
        return self._handle_request("GET", "/api/households/mealplans/today")

    def create_random_meal(self, random_meal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a random meal plan entry based on rules defined in the household's mealplan settings.

        Args:
            random_meal_data: Dictionary containing at minimum a date field and optionally an entryType field:
                - date: Required. ISO format date string (YYYY-MM-DD)
                - entryType: Optional. One of 'breakfast', 'lunch', 'dinner', 'side'

        Returns:
            Dict containing the created meal plan entry with a randomly selected recipe
        """
        return self._handle_request(
            "POST", "/api/households/mealplans/random", json=random_meal_data
        )

    def get_mealplan_rules(
        self,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get all meal plan rules.

        Args:
            page: Optional page number for pagination
            per_page: Optional number of items per page

        Returns:
            Dict containing meal plan rules and pagination information
        """
        params = ParamBuilder()
        if page is not None:
            params.add("page", page)
        if per_page is not None:
            params.add("per_page", per_page)

        return self._handle_request(
            "GET", "/api/households/mealplans/rules", params=params.build()
        )

    def get_mealplan_rule(self, rule_id: str) -> Dict[str, Any]:
        """
        Get a specific meal plan rule by ID.

        Args:
            rule_id: The UUID of the meal plan rule

        Returns:
            Dict containing meal plan rule details
        """
        return self._handle_request(
            "GET", f"/api/households/mealplans/rules/{rule_id}"
        )

    def create_mealplan_rule(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new meal plan rule.

        Args:
            rule_data: Dictionary containing meal plan rule details with the following fields:
                - day: Optional. One of 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'unset'
                - entryType: Optional. One of 'breakfast', 'lunch', 'dinner', 'side', 'unset'
                - queryFilterString: Optional. Query filter for recipe selection

        Returns:
            Dict containing the created meal plan rule
        """
        return self._handle_request(
            "POST", "/api/households/mealplans/rules", json=rule_data
        )

    def update_mealplan_rule(
        self, rule_id: str, rule_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing meal plan rule.

        Args:
            rule_id: The UUID of the meal plan rule to update
            rule_data: Dictionary containing meal plan rule fields to update

        Returns:
            Dict containing the updated meal plan rule
        """
        return self._handle_request(
            "PUT", f"/api/households/mealplans/rules/{rule_id}", json=rule_data
        )