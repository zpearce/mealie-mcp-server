from typing import List

from fastmcp import FastMCP
from fastmcp.prompts import AssistantMessage, Message, UserMessage


def register_prompts(mcp: FastMCP) -> None:
    """Register all prompt-related tools with the MCP server."""

    @mcp.prompt()
    def weekly_meal_plan(preferences: str = "") -> list[Message]:
        """Generates a weekly meal plan template.

        Args:
            preferences: Additional dietary preferences or constraints
        """
        # System message with detailed instructions for the AI assistant
        system_content = """
<context>
You have access to a Mealie recipe database with various recipes. You can search for recipes and create meal plans that can be saved directly to the Mealie system.
</context>

<instructions>
# Meal Planning Guidelines
- Include breakfast, lunch, and dinner for all 7 days
- Create a variety of meals using different proteins, grains, and vegetables
- Consider seasonal ingredients
- Balance nutrition throughout the week
- Use recipes from the Mealie database when available

# Leftover Management
- Plan for leftovers where appropriate (e.g., making extra portions of dinner that can be used for lunch the next day)
- When planning leftovers, suggest how the leftover meal can be repurposed or enhanced

# Recipe Format
When suggesting recipes from the Mealie database, include the recipe ID or slug if available.

# User Feedback Process
After presenting the meal plan, ask the user for specific feedback about:
- Present the meal plan in table format
- Whether any meals should be swapped or adjusted
- If the leftover utilization works for their schedule
- Any additional dietary needs that weren't addressed

# Saving to Mealie
Once the user is satisfied with the meal plan:
1. Ask if they want to save it to their Mealie database
2. Provide a concise summary in table format
3. When saving to Mealie, use the recipe_id parameter for any Mealie recipes
</instructions>
"""

        # User message that initiates the conversation
        user_content = "I need help creating a balanced meal plan for the next week that includes breakfast, lunch, and dinner."

        if preferences:
            user_content += f" My preferences are: {preferences}"

        # Create and return a list of Message objects
        return [
            AssistantMessage(system_content),
            UserMessage(user_content),
        ]
