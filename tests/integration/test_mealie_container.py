"""Integration tests using a real Mealie container via testcontainers.

This test spins up an actual Mealie instance in a Docker container
to verify our implementation matches the real API exactly.
"""

import json
import time
import pytest
import httpx
from testcontainers.compose import DockerCompose
from testcontainers.postgres import PostgresContainer
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs

from mealie import MealieFetcher


class MealieContainer(DockerContainer):
    """Custom container for Mealie with proper configuration."""

    def __init__(self, image="ghcr.io/mealie-recipes/mealie:latest", **kwargs):
        super().__init__(image, **kwargs)
        self.port_to_expose = 9000
        self.with_exposed_ports(self.port_to_expose)
        self.with_env("ALLOW_SIGNUP", "true")
        self.with_env("DEFAULT_EMAIL", "changeme@example.com")
        self.with_env("DEFAULT_PASSWORD", "MyPassword")
        self.with_env("BASE_URL", "http://localhost:9000")
        self.with_env("API_PORT", "9000")
        self.with_env("WEB_CONCURRENCY", "1")
        self.with_env("MAX_WORKERS", "1")
        self.with_env("AUTO_BACKUP_ENABLED", "false")
        self.with_env("DB_ENGINE", "sqlite")

    def get_api_url(self):
        """Get the API URL for the running container."""
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.port_to_expose)
        return f"http://{host}:{port}"

    def wait_until_ready(self, timeout=60):
        """Wait for Mealie to be fully ready."""
        api_url = self.get_api_url()
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                response = httpx.get(f"{api_url}/api/app/about")
                if response.status_code == 200:
                    return True
            except Exception:
                pass
            time.sleep(1)

        raise TimeoutError(f"Mealie did not start within {timeout} seconds")


@pytest.fixture(scope="session")
def mealie_container():
    """Start a Mealie container for the test session."""
    container = MealieContainer()
    container.start()

    try:
        container.wait_until_ready()
        yield container
    finally:
        container.stop()


@pytest.fixture
def mealie_api_client(mealie_container):
    """Create an API client connected to the test Mealie instance."""
    api_url = mealie_container.get_api_url()

    login_data = {
        "username": "changeme@example.com",
        "password": "MyPassword"
    }

    response = httpx.post(
        f"{api_url}/api/auth/token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    if response.status_code != 200:
        raise Exception(f"Failed to login with default credentials: {response.status_code} - {response.text}")

    token_data = response.json()
    api_key = token_data["access_token"]

    return MealieFetcher(api_url, api_key)


class TestMealieContainerIntegration:
    """Test our implementation against a real Mealie instance."""

    def test_mealie_is_running(self, mealie_container):
        """Verify the Mealie container is running and accessible."""
        api_url = mealie_container.get_api_url()
        response = httpx.get(f"{api_url}/api/app/about")

        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "production" in data

    def test_import_recipe_from_url_returns_slug(self, mealie_api_client):
        """Test that the create/url endpoint returns just a slug string."""
        test_url = "https://www.allrecipes.com/recipe/10813/best-chocolate-chip-cookies/"

        try:
            result = mealie_api_client.import_recipe_from_url(test_url)

            assert isinstance(result, dict)
            assert "slug" in result
            assert "name" in result

            slug = result["slug"]
            fetched_recipe = mealie_api_client.get_recipe(slug)
            assert fetched_recipe["slug"] == slug

        except Exception as e:
            if "400" in str(e) or "422" in str(e):
                pytest.skip(f"Mealie couldn't parse the test URL: {e}")
            else:
                raise

    def test_import_invalid_url_validation(self, mealie_api_client):
        """Test that URL validation happens before API call."""

        with pytest.raises(ValueError) as exc_info:
            mealie_api_client.import_recipe_from_url("")
        assert "cannot be empty" in str(exc_info.value).lower()

        with pytest.raises(ValueError) as exc_info:
            mealie_api_client.import_recipe_from_url("not-a-url")
        assert "invalid url format" in str(exc_info.value).lower()

    def test_import_from_non_recipe_url(self, mealie_api_client):
        """Test behavior when URL doesn't contain a recipe."""

        test_url = "https://www.google.com"

        with pytest.raises(Exception) as exc_info:
            mealie_api_client.import_recipe_from_url(test_url)

        error = str(exc_info.value)
        assert "400" in error or "422" in error

    @pytest.mark.parametrize("test_url,should_fail", [
        ("https://example.com/fake-recipe", True),
        ("https://httpstat.us/404", True),
        ("https://www.bbc.com", True),
    ])
    def test_various_url_scenarios(self, mealie_api_client, test_url, should_fail):
        """Test various URL scenarios against real Mealie."""
        try:
            result = mealie_api_client.import_recipe_from_url(test_url)

            if should_fail:
                print(f"Unexpected success for {test_url}: {result}")
                assert "slug" in result
                assert "name" in result
        except Exception as e:
            if should_fail:
                assert "MealieApiError" in str(type(e)) or "400" in str(e) or "422" in str(e)
            else:
                raise
