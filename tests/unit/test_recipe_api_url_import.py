"""Unit tests for the recipe URL import API method."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from mealie import MealieFetcher


class TestRecipeUrlImportAPI:
    """Test the import_recipe_from_url API method."""

    @patch('mealie.client.httpx.Client')
    def test_import_recipe_from_url_success(self, mock_client_class):
        """Test successful recipe import from URL."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        fetcher = MealieFetcher("http://test.local", "test-key")

        expected_response = {
            "id": "recipe-123",
            "slug": "imported-recipe",
            "name": "Imported Recipe",
            "orgURL": "https://example.com/recipe",
        }

        fetcher._handle_request = Mock(side_effect=["imported-recipe", expected_response])
        result = fetcher.import_recipe_from_url("https://example.com/recipe")

        assert fetcher._handle_request.call_count == 2
        fetcher._handle_request.assert_any_call(
            "POST",
            "/api/recipes/create/url",
            json={"url": "https://example.com/recipe"}
        )
        fetcher._handle_request.assert_any_call(
            "GET",
            "/api/recipes/imported-recipe"
        )

        assert result == expected_response
        assert result["slug"] == "imported-recipe"
        assert result["orgURL"] == "https://example.com/recipe"

    @patch('mealie.client.httpx.Client')
    def test_import_recipe_from_url_validates_url(self, mock_client_class):
        """Test that URL validation happens before API call."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        fetcher = MealieFetcher("http://test.local", "test-key")
        fetcher._handle_request = Mock()

        with pytest.raises(ValueError) as exc_info:
            fetcher.import_recipe_from_url("")
        assert "url cannot be empty" in str(exc_info.value).lower()

        with pytest.raises(ValueError) as exc_info:
            fetcher.import_recipe_from_url("not-a-url")
        assert "invalid url format" in str(exc_info.value).lower()

        fetcher._handle_request.assert_not_called()

    @patch('mealie.client.httpx.Client')
    def test_import_recipe_from_url_handles_api_errors(self, mock_client_class):
        """Test that API errors are properly propagated."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        fetcher = MealieFetcher("http://test.local", "test-key")

        from mealie.client import MealieApiError
        fetcher._handle_request = Mock(
            side_effect=MealieApiError(400, "Unable to scrape recipe", "Bad Request")
        )

        with pytest.raises(MealieApiError) as exc_info:
            fetcher.import_recipe_from_url("https://example.com/recipe")

        assert exc_info.value.status_code == 400
        assert "Unable to scrape recipe" in str(exc_info.value)

    @patch('mealie.client.httpx.Client')
    def test_import_recipe_from_url_normalizes_url(self, mock_client_class):
        """Test that URLs are normalized before sending."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        fetcher = MealieFetcher("http://test.local", "test-key")

        def mock_handler(*args, **kwargs):
            if args[0] == "POST":
                return "test"
            else:
                return {"slug": "test", "name": "Test Recipe"}

        fetcher._handle_request = Mock(side_effect=mock_handler)

        test_cases = [
            ("https://example.com/recipe", "https://example.com/recipe"),
            ("http://example.com/recipe", "http://example.com/recipe"),
            ("https://example.com/recipe?param=1", "https://example.com/recipe?param=1"),
            ("  https://example.com/recipe  ", "https://example.com/recipe"),
        ]

        for input_url, expected_url in test_cases:
            fetcher._handle_request.reset_mock()
            fetcher.import_recipe_from_url(input_url)

            assert fetcher._handle_request.call_count == 2
            fetcher._handle_request.assert_any_call(
                "POST",
                "/api/recipes/create/url",
                json={"url": expected_url}
            )

    @patch('mealie.client.httpx.Client')
    def test_import_recipe_from_url_timeout_handling(self, mock_client_class):
        """Test handling of timeout during import."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        fetcher = MealieFetcher("http://test.local", "test-key")

        fetcher._handle_request = Mock(side_effect=TimeoutError("Request timed out"))

        with pytest.raises(TimeoutError):
            fetcher.import_recipe_from_url("https://slow-site.com/recipe")

    @patch('mealie.client.httpx.Client')
    def test_import_recipe_from_url_connection_error(self, mock_client_class):
        """Test handling of connection errors."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        fetcher = MealieFetcher("http://test.local", "test-key")

        fetcher._handle_request = Mock(side_effect=ConnectionError("Failed to connect"))

        with pytest.raises(ConnectionError):
            fetcher.import_recipe_from_url("https://offline-site.com/recipe")

    @patch('mealie.client.httpx.Client')
    def test_import_recipe_from_url_with_special_url_chars(self, mock_client_class):
        """Test URLs with special characters are handled correctly."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        fetcher = MealieFetcher("http://test.local", "test-key")

        fetcher._handle_request = Mock(side_effect=[
            "test",
            {"slug": "test", "name": "Test Recipe"}
        ])

        url = "https://example.com/recipes/crème-brûlée"
        fetcher.import_recipe_from_url(url)

        assert fetcher._handle_request.call_count == 2
        fetcher._handle_request.assert_any_call(
            "POST",
            "/api/recipes/create/url",
            json={"url": url}
        )
        fetcher._handle_request.assert_any_call(
            "GET",
            "/api/recipes/test"
        )

    @patch('mealie.client.httpx.Client')
    def test_import_recipe_from_url_logging(self, mock_client_class):
        """Test that appropriate logging happens."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        fetcher = MealieFetcher("http://test.local", "test-key")

        fetcher._handle_request = Mock(side_effect=[
            "test-recipe",
            {"slug": "test-recipe", "name": "Test Recipe"}
        ])

        with patch("mealie.recipe.logger") as mock_logger:
            fetcher.import_recipe_from_url("https://example.com/recipe")

            assert mock_logger.info.call_count >= 1
            mock_logger.info.assert_any_call({
                "message": "Importing recipe from URL",
                "url": "https://example.com/recipe"
            })
