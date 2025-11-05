"""Immich API client."""

import re
from typing import Optional

import httpx
from rich.console import Console

from immich_janitor.models import Asset, AssetBulkDeleteRequest

console = Console()


class ImmichClient:
    """Client for interacting with Immich API."""

    def __init__(self, api_url: str, api_key: str):
        """Initialize the client.
        
        Args:
            api_url: Base URL for Immich API (e.g., http://localhost:2283/api)
            api_key: API key for authentication
        """
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.headers = {
            "X-Api-Key": api_key,
            "Accept": "application/json",
        }
        self.client = httpx.Client(headers=self.headers, timeout=30.0)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> httpx.Response:
        """Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            endpoint: API endpoint (e.g., /assets)
            **kwargs: Additional arguments for httpx request
            
        Returns:
            Response object
            
        Raises:
            httpx.HTTPError: If the request fails
        """
        url = f"{self.api_url}{endpoint}"
        
        try:
            response = self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPError as e:
            console.print(f"[red]HTTP Error: {e}[/red]")
            raise

    def get_all_assets(
        self,
        limit: Optional[int] = None,
        pattern: Optional[str] = None,
    ) -> list[Asset]:
        """Get all assets from Immich library.
        
        Args:
            limit: Maximum number of assets to return
            pattern: Regex pattern to filter assets by filename
            
        Returns:
            List of Asset objects
        """
        # Note: The actual Immich API might paginate results differently
        # This is a simplified implementation
        response = self._make_request("GET", "/assets")
        
        assets_data = response.json()
        assets = [Asset(**asset_data) for asset_data in assets_data]
        
        # Filter by pattern if provided
        if pattern:
            regex = re.compile(pattern)
            assets = [
                asset
                for asset in assets
                if regex.search(asset.original_file_name)
            ]
        
        # Apply limit if provided
        if limit:
            assets = assets[:limit]
        
        return assets

    def delete_assets(self, asset_ids: list[str], force: bool = False) -> None:
        """Delete multiple assets.
        
        Args:
            asset_ids: List of asset IDs to delete
            force: If True, permanently delete assets (bypass trash)
        """
        request_data = AssetBulkDeleteRequest(ids=asset_ids, force=force)
        
        self._make_request(
            "DELETE",
            "/assets",
            json=request_data.model_dump(),
        )

    def get_asset_info(self, asset_id: str) -> Asset:
        """Get information about a specific asset.
        
        Args:
            asset_id: Asset ID
            
        Returns:
            Asset object
        """
        response = self._make_request("GET", f"/assets/{asset_id}")
        return Asset(**response.json())

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
