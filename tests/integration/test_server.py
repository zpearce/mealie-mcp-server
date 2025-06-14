"""Integration tests for the MCP server."""

import pytest
from fastmcp import Client

from tests.conftest import create_test_server


@pytest.mark.asyncio
async def test_server_initialization(test_env, httpx_mock):
    """Test that the server initializes correctly with all tools."""
    # Create server after setting up initial mock
    mcp_server = create_test_server(httpx_mock)
    
    async with Client(mcp_server) as client:
        # List available tools
        tools = await client.list_tools()
        
        # Get tool names (tools is a list, not an object)
        tool_names = [tool.name for tool in tools]
        
        # Verify expected tools are registered
        expected_tools = [
            "get_recipes",
            "get_recipe_concise", 
            "get_recipe_detailed",
            "create_recipe",
            "update_recipe",
            "get_all_mealplans",
            "create_mealplan",
            "get_todays_mealplan",
            "create_mealplan_bulk",
        ]
        
        for tool in expected_tools:
            assert tool in tool_names, f"Tool {tool} not found in registered tools"


@pytest.mark.asyncio
async def test_server_prompts(test_env, httpx_mock):
    """Test that prompts are registered correctly."""
    # Create server after setting up initial mock
    mcp_server = create_test_server(httpx_mock)
    
    async with Client(mcp_server) as client:
        # List available prompts
        prompts = await client.list_prompts()
        
        # Get prompt names (prompts is a list, not an object)
        prompt_names = [prompt.name for prompt in prompts]
        
        # Verify weekly meal plan prompt is registered
        assert "weekly_meal_plan" in prompt_names


@pytest.mark.asyncio
async def test_prompt_generation(test_env, httpx_mock):
    """Test that prompts generate expected messages."""
    # Create server after setting up initial mock
    mcp_server = create_test_server(httpx_mock)
    
    async with Client(mcp_server) as client:
        # Get the weekly meal plan prompt
        prompt_result = await client.get_prompt(
            "weekly_meal_plan",
            {"preferences": "vegetarian, gluten-free"}
        )
        
        # Verify the prompt contains expected content
        messages = prompt_result.messages
        assert len(messages) == 2
        
        # Check system message contains instructions
        system_msg = messages[0].content.text
        assert "Mealie recipe database" in system_msg
        assert "Tool Usage Guidelines" in system_msg
        
        # Check user message contains preferences
        user_msg = messages[1].content.text
        assert "balanced meal plan" in user_msg
        assert "vegetarian, gluten-free" in user_msg