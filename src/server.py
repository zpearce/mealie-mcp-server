import os
from dotenv import load_dotenv
from mealie_client import MealieClient
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mealie")

load_dotenv()
MEALIE_BASE_URL = os.getenv("MEALIE_BASE_URL")
MEALIE_API_KEY = os.getenv("MEALIE_API_KEY")

mealie = MealieClient(
    base_url=MEALIE_BASE_URL,
    api_key=MEALIE_API_KEY,
)


@mcp.tool(description="Provides paginated list of foods")
def get_foods() -> str:
    return mealie.get_foods()


if __name__ == "__main__":
    mcp.run(transport="stdio")
