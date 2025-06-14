"""Unit tests for utility functions."""

import json

from utils import format_api_params, format_error_response


def test_format_error_response():
    """Test error response formatting."""
    error_msg = "Something went wrong"
    result = format_error_response(error_msg)
    
    # Parse JSON response
    parsed = json.loads(result)
    
    assert parsed["success"] is False
    assert parsed["error"] == error_msg


def test_format_api_params_with_lists():
    """Test API parameter formatting with list values."""
    params = {
        "tags": ["vegetarian", "quick-meal"],
        "categories": ["Dinner", "Main Course"],
        "page": 1,
        "per_page": 20,
    }
    
    result = format_api_params(params)
    
    assert result["tags"] == "vegetarian,quick-meal"
    assert result["categories"] == "Dinner,Main Course"
    assert result["page"] == 1
    assert result["per_page"] == 20


def test_format_api_params_with_none_values():
    """Test API parameter formatting filters out None values."""
    params = {
        "query": "chicken",
        "tags": None,
        "categories": None,
        "page": 1,
    }
    
    result = format_api_params(params)
    
    assert result == {"query": "chicken", "page": 1}
    assert "tags" not in result
    assert "categories" not in result


def test_format_api_params_empty_list():
    """Test API parameter formatting with empty lists."""
    params = {
        "tags": [],
        "query": "test",
    }
    
    result = format_api_params(params)
    
    assert result["tags"] == ""
    assert result["query"] == "test"