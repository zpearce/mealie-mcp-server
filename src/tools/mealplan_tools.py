import logging
import traceback
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from utils import format_error_response
from mealie import MealieFetcher

logger = logging.getLogger("mealie-mcp")


def register_mealplan_tools(mcp: FastMCP, mealie: MealieFetcher) -> None:
    """Register all mealplan-related tools with the MCP server."""

    @mcp.tool()
    def get_mealplans(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> str:
        """Get a list of meal plan entries, optionally filtered by date range.

        Args:
            start_date: Optional ISO format date (YYYY-MM-DD) to start from
            end_date: Optional ISO format date (YYYY-MM-DD) to end at
            page: Page number for pagination
            per_page: Number of items per page

        Returns:
            str: Meal plan entries with pagination information.

        Example:
            To get meal plans for a specific date range:
            get_mealplans(start_date="2025-04-01", end_date="2025-04-07")
        """
        try:
            logger.info(
                f"Fetching meal plans with start_date: {start_date}, end_date: {end_date}, page: {page}, per_page: {per_page}"
            )
            return mealie.get_all_mealplans(
                start_date=start_date,
                end_date=end_date,
                page=page,
                per_page=per_page,
            )
        except Exception as e:
            error_msg = f"Error fetching meal plans: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)

    @mcp.tool()
    def get_mealplan(item_id: int) -> str:
        """Get a specific meal plan entry by ID.

        Args:
            item_id: The numeric ID of the meal plan entry to retrieve

        Returns:
            str: Complete meal plan entry details including date, title, and any associated recipe.
        """
        try:
            logger.info(f"Fetching meal plan with ID: {item_id}")
            return mealie.get_mealplan(item_id)
        except Exception as e:
            error_msg = f"Error fetching meal plan with ID {item_id}: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)

    @mcp.tool()
    def create_mealplan(mealplan_data: Dict[str, Any]) -> str:
        """Create a new meal plan entry.

        Args:
            mealplan_data: A dictionary containing meal plan details with the following fields:
                - date: Required. ISO format date string (YYYY-MM-DD)
                - entryType: Optional. One of 'breakfast', 'lunch', 'dinner', 'side'
                - title: Optional. Title for the meal
                - text: Optional. Text description
                - recipeId: Optional. UUID of a recipe if this entry is linked to a recipe

        Returns:
            str: The created meal plan entry details.

        Example:
            To create a lunch entry for a specific date:
            ```json
            {
              "date": "2025-04-20",
              "entryType": "lunch",
              "title": "Caesar Salad",
              "text": "With homemade dressing"
            }
            ```

            To create an entry linked to a recipe:
            ```json
            {
              "date": "2025-04-20",
              "entryType": "dinner",
              "recipeId": "1a2b3c4d-5e6f-7g8h-9i0j-klmnopqrstuv"
            }
            ```
        """
        try:
            logger.info(f"Creating new meal plan entry: {mealplan_data}")
            return mealie.create_mealplan(mealplan_data)
        except Exception as e:
            error_msg = f"Error creating meal plan: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)

    @mcp.tool()
    def update_mealplan(item_id: int, mealplan_data: Dict[str, Any]) -> str:
        """Update an existing meal plan entry.

        Args:
            item_id: The numeric ID of the meal plan entry to update
            mealplan_data: A dictionary containing the meal plan fields to update

        Returns:
            str: The updated meal plan entry details.

        Example:
            To update a meal plan entry's title and entry type:
            ```json
            {
              "item_id": 123,
              "mealplan_data": {
                "title": "Updated Meal Title",
                "entryType": "dinner"
              }
            }
            ```
        """
        try:
            logger.info(f"Updating meal plan with ID {item_id}: {mealplan_data}")
            return mealie.update_mealplan(item_id, mealplan_data)
        except Exception as e:
            error_msg = f"Error updating meal plan with ID {item_id}: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)

    @mcp.tool()
    def get_todays_meals() -> str:
        """Get all meal plan entries for today.

        Returns:
            str: List of meal plan entries for the current day.
        """
        try:
            logger.info("Fetching today's meal plan entries")
            return mealie.get_todays_meals()
        except Exception as e:
            error_msg = f"Error fetching today's meal plans: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)

    @mcp.tool()
    def create_random_meal(random_meal_data: Dict[str, Any]) -> str:
        """Create a random meal plan entry based on household mealplan rules.

        The meal will be selected randomly based on rules defined in the household's
        mealplan settings. If no settings are defined, it will return any random meal.

        Args:
            random_meal_data: A dictionary containing at minimum a date field:
                - date: Required. ISO format date string (YYYY-MM-DD)
                - entryType: Optional. One of 'breakfast', 'lunch', 'dinner', 'side'

        Returns:
            str: The created meal plan entry with a randomly selected recipe.

        Example:
            To create a random dinner for a specific date:
            ```json
            {
              "date": "2025-04-20",
              "entryType": "dinner"
            }
            ```
        """
        try:
            logger.info(f"Creating random meal plan entry: {random_meal_data}")
            return mealie.create_random_meal(random_meal_data)
        except Exception as e:
            error_msg = f"Error creating random meal: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)

    @mcp.tool()
    def get_mealplan_rules(
        page: Optional[int] = None, per_page: Optional[int] = None
    ) -> str:
        """Get all meal plan rules with pagination support.

        Meal plan rules determine how random meals are selected when using the
        create_random_meal tool.

        Args:
            page: Page number for pagination
            per_page: Number of items per page

        Returns:
            str: List of meal plan rules with pagination information.
        """
        try:
            logger.info(
                f"Fetching meal plan rules with page: {page}, per_page: {per_page}"
            )
            return mealie.get_mealplan_rules(page=page, per_page=per_page)
        except Exception as e:
            error_msg = f"Error fetching meal plan rules: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)

    @mcp.tool()
    def get_mealplan_rule(rule_id: str) -> str:
        """Get a specific meal plan rule by ID.

        Args:
            rule_id: The UUID of the meal plan rule to retrieve

        Returns:
            str: Complete meal plan rule details.
        """
        try:
            logger.info(f"Fetching meal plan rule with ID: {rule_id}")
            return mealie.get_mealplan_rule(rule_id)
        except Exception as e:
            error_msg = f"Error fetching meal plan rule with ID {rule_id}: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)

    @mcp.tool()
    def create_mealplan_rule(rule_data: Dict[str, Any]) -> str:
        """Create a new meal plan rule.

        Meal plan rules determine how random meals are selected when using the
        create_random_meal tool.

        Args:
            rule_data: A dictionary containing meal plan rule details with the following fields:
                - day: Optional. One of 'monday', 'tuesday', 'wednesday', 'thursday',
                  'friday', 'saturday', 'sunday', 'unset'
                - entryType: Optional. One of 'breakfast', 'lunch', 'dinner', 'side', 'unset'
                - queryFilterString: Optional. Query filter for recipe selection

        Returns:
            str: The created meal plan rule details.

        Example:
            To create a rule for dinner on Fridays:
            ```json
            {
              "day": "friday",
              "entryType": "dinner",
              "queryFilterString": "categories:italian"
            }
            ```
        """
        try:
            logger.info(f"Creating new meal plan rule: {rule_data}")
            return mealie.create_mealplan_rule(rule_data)
        except Exception as e:
            error_msg = f"Error creating meal plan rule: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)

    @mcp.tool()
    def update_mealplan_rule(rule_id: str, rule_data: Dict[str, Any]) -> str:
        """Update an existing meal plan rule.

        Args:
            rule_id: The UUID of the meal plan rule to update
            rule_data: A dictionary containing the meal plan rule fields to update

        Returns:
            str: The updated meal plan rule details.

        Example:
            To update a meal plan rule's day and query filter:
            ```json
            {
              "rule_id": "1a2b3c4d-5e6f-7g8h-9i0j-klmnopqrstuv",
              "rule_data": {
                "day": "monday",
                "queryFilterString": "categories:mexican"
              }
            }
            ```
        """
        try:
            logger.info(f"Updating meal plan rule with ID {rule_id}: {rule_data}")
            return mealie.update_mealplan_rule(rule_id, rule_data)
        except Exception as e:
            error_msg = f"Error updating meal plan rule with ID {rule_id}: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            return format_error_response(error_msg)
