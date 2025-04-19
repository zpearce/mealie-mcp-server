import json
import logging
import traceback
from typing import Any, Dict

import httpx
from httpx import ConnectError, HTTPStatusError, ReadTimeout

logger = logging.getLogger("mealie-mcp")


class MealieApiError(Exception):
    """Custom exception for Mealie API errors with status code and response details."""

    def __init__(self, status_code: int, message: str, response_text: str = None):
        self.status_code = status_code
        self.message = message
        self.response_text = response_text
        super().__init__(f"{message} (Status Code: {status_code})")


class MealieClient:

    def __init__(self, base_url: str, api_key: str):
        if not base_url:
            raise ValueError("Base URL cannot be empty")
        if not api_key:
            raise ValueError("API key cannot be empty")

        logger.debug(f"Initializing MealieClient with base URL: {base_url}")
        try:
            self._client = httpx.Client(
                base_url=base_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                timeout=30.0,  # Set a reasonable timeout for requests
            )
            # Test connection
            logger.debug("Testing connection to Mealie API")
            self._client.get("/api/app/about")
            logger.info("Successfully connected to Mealie API")
        except ConnectError as e:
            error_msg = f"Failed to connect to Mealie API at {base_url}: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            raise ConnectionError(error_msg) from e
        except Exception as e:
            error_msg = f"Error initializing Mealie client: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            raise

    def _handle_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Common request handler with error handling for all API calls."""
        try:
            logger.debug(f"Making {method} request to {url}")

            if "params" in kwargs:
                logger.debug(f"Request parameters: {kwargs['params']}")
            if "json" in kwargs:
                logger.debug(f"Request payload: {kwargs['json']}")

            response = self._client.request(method, url, **kwargs)
            response.raise_for_status()  # Raise an exception for 4XX/5XX responses

            logger.debug(f"Request successful: {response.status_code}")
            return response.json()

        except HTTPStatusError as e:
            status_code = e.response.status_code
            error_detail = f"HTTP Error {status_code}"

            # Try to parse error details from response
            try:
                error_detail = e.response.json()
            except Exception:
                error_detail = e.response.text

            error_msg = f"API error for {method} {url}: {error_detail}"
            logger.error(error_msg)
            logger.debug(f"Failed Request body: {e.request.content}")
            raise MealieApiError(status_code, error_msg, e.response.text) from e

        except ReadTimeout:
            error_msg = f"Request timeout for {method} {url}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            raise TimeoutError(error_msg)

        except ConnectError as e:
            error_msg = f"Connection error for {method} {url}: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            raise ConnectionError(error_msg) from e

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse response as JSON: {str(e)}")
            logger.debug(f"Non-JSON response text: {e.response.text}")
            return {"raw_response": response.text}

        except Exception as e:
            error_msg = f"Unexpected error for {method} {url}: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            raise
