"""FHIR server client for posting resources."""

import os
from typing import Optional

import requests
from fhir.resources.bundle import Bundle


class FHIRClient:
    """Client for interacting with FHIR servers."""

    def __init__(
        self,
        server_url: Optional[str] = None,
        auth_token: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Initialize FHIR client.

        Args:
            server_url: FHIR server base URL (defaults to FHIR_SERVER_URL env var)
            auth_token: Optional authentication token (defaults to FHIR_SERVER_AUTH_TOKEN env var)
            timeout: Request timeout in seconds
        """
        self.server_url = (server_url or os.getenv("FHIR_SERVER_URL", "")).rstrip("/")
        if not self.server_url:
            raise ValueError("FHIR server URL is required")

        self.auth_token = auth_token or os.getenv("FHIR_SERVER_AUTH_TOKEN")
        self.timeout = timeout

        # Set up headers
        self.headers = {
            "Content-Type": "application/fhir+json",
            "Accept": "application/fhir+json",
        }

        if self.auth_token:
            self.headers["Authorization"] = f"Bearer {self.auth_token}"

    def post_bundle(self, bundle: Bundle) -> dict:
        """
        POST a transaction Bundle to the FHIR server.

        Args:
            bundle: FHIR transaction Bundle to post

        Returns:
            Server response as dictionary

        Raises:
            requests.exceptions.RequestException: If the request fails
            ValueError: If the server returns an error
        """
        # Convert bundle to JSON
        bundle_json = bundle.model_dump_json(exclude_none=True)

        # POST to server
        try:
            response = requests.post(
                self.server_url,
                data=bundle_json,
                headers=self.headers,
                timeout=self.timeout,
            )

            # Raise exception for bad status codes
            response.raise_for_status()

            # Return response as dictionary
            return response.json()

        except requests.exceptions.HTTPError as e:
            error_msg = f"FHIR server returned error: {e}"
            if e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg += f"\nDetails: {error_detail}"
                except Exception:
                    error_msg += f"\nResponse: {e.response.text}"
            raise ValueError(error_msg) from e

        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(
                f"Failed to connect to FHIR server: {e}"
            ) from e

    def post_bundle_json(self, bundle_json: str) -> dict:
        """
        POST a transaction Bundle (as JSON string) to the FHIR server.

        Args:
            bundle_json: FHIR transaction Bundle as JSON string

        Returns:
            Server response as dictionary

        Raises:
            requests.exceptions.RequestException: If the request fails
            ValueError: If the server returns an error
        """
        try:
            response = requests.post(
                self.server_url,
                data=bundle_json,
                headers=self.headers,
                timeout=self.timeout,
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            error_msg = f"FHIR server returned error: {e}"
            if e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg += f"\nDetails: {error_detail}"
                except Exception:
                    error_msg += f"\nResponse: {e.response.text}"
            raise ValueError(error_msg) from e

        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(
                f"Failed to connect to FHIR server: {e}"
            ) from e

    def test_connection(self) -> bool:
        """
        Test connection to FHIR server.

        Returns:
            True if server is reachable, False otherwise
        """
        try:
            # Try to get the CapabilityStatement (metadata endpoint)
            response = requests.get(
                f"{self.server_url}/metadata",
                headers={"Accept": "application/fhir+json"},
                timeout=self.timeout,
            )
            return response.status_code == 200
        except Exception:
            return False
