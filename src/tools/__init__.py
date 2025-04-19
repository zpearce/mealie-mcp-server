from .group_tools import register_group_tools
from .recipe_tools import register_recipe_tools
from .user_tools import register_user_tools


def register_all_tools(mcp, mealie):
    """Register all tools with the MCP server."""
    register_recipe_tools(mcp, mealie)
    register_user_tools(mcp, mealie)
    register_group_tools(mcp, mealie)


__all__ = [
    "register_all_tools",
    "register_recipe_tools",
    "register_user_tools",
    "register_group_tools",
]
