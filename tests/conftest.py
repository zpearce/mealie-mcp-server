"""Shared pytest fixtures for mealie-mcp-server tests."""

import os
import sys
from pathlib import Path

import pytest
from fastmcp import Client, FastMCP
from pytest_httpx import HTTPXMock

# Add src to Python path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def test_env(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("MEALIE_BASE_URL", "http://test.mealie.local")
    monkeypatch.setenv("MEALIE_API_KEY", "test-api-key-12345")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")


def create_test_server(httpx_mock):
    """Helper function to create a test server with mocked connection."""
    # Import here to ensure proper initialization order
    from mealie import MealieFetcher
    from prompts import register_prompts
    from tools import register_all_tools

    # Mock the initial connection check that happens during MealieFetcher init
    httpx_mock.add_response(
        url="http://test.mealie.local/api/app/about",
        json={"version": "1.0.0", "name": "Mealie"},
    )
    
    # Create test server
    mcp = FastMCP("test-mealie-server")
    
    # Create MealieFetcher with test credentials
    mealie = MealieFetcher(
        base_url=os.getenv("MEALIE_BASE_URL"),
        api_key=os.getenv("MEALIE_API_KEY"),
    )
    
    # Register prompts and tools
    register_prompts(mcp)
    register_all_tools(mcp, mealie)
    
    return mcp