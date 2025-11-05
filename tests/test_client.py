"""Tests for Immich API client."""

from unittest.mock import Mock, patch

import pytest
import httpx

from immich_janitor.client import ImmichClient
from immich_janitor.models import Asset


@pytest.fixture
def mock_client():
    """Create a mock client for testing."""
    return ImmichClient(
        api_url="http://test.local:2283/api",
        api_key="test-api-key",
    )


@pytest.fixture
def sample_asset_data():
    """Sample asset data for testing."""
    return {
        "id": "asset-123",
        "originalFileName": "test.jpg",
        "type": "IMAGE",
        "createdAt": "2024-01-01T12:00:00Z",
        "exifInfo": {
            "fileSizeInByte": 5000000,
            "exifImageWidth": 1920,
            "exifImageHeight": 1080,
        },
        "isFavorite": False,
        "isArchived": False,
        "isTrashed": False,
    }


def test_client_initialization(mock_client):
    """Test client is initialized correctly."""
    assert mock_client.api_url == "http://test.local:2283/api"
    assert mock_client.api_key == "test-api-key"
    assert "x-api-key" in mock_client.headers
    assert mock_client.headers["x-api-key"] == "test-api-key"


def test_api_url_trailing_slash():
    """Test that trailing slash is removed from API URL."""
    client = ImmichClient(
        api_url="http://test.local:2283/api/",
        api_key="test-key",
    )
    assert client.api_url == "http://test.local:2283/api"


def test_get_all_assets_single_page(mock_client, sample_asset_data):
    """Test fetching assets - single page (less than 1000)."""
    with patch.object(mock_client, '_make_request') as mock_request:
        # Mock response with less than 1000 assets
        mock_response = Mock()
        mock_response.json.return_value = {
            "assets": {
                "items": [sample_asset_data] * 500,  # 500 assets
                "total": 500,
            }
        }
        mock_request.return_value = mock_response
        
        assets = mock_client.get_all_assets()
        
        assert len(assets) == 500
        assert all(isinstance(asset, Asset) for asset in assets)
        # Should call only once (single page)
        assert mock_request.call_count == 1
        
        # Verify withExif parameter is passed
        call_args = mock_request.call_args
        assert call_args[1]['json']['withExif'] is True


def test_get_all_assets_pagination(mock_client, sample_asset_data):
    """Test fetching assets with pagination - multiple pages.
    
    This is a regression test for the pagination bug where only
    1000 assets were fetched.
    """
    with patch.object(mock_client, '_make_request') as mock_request:
        # Mock 3 pages: 1000, 1000, 500 = 2500 total
        responses = [
            # Page 1: full page
            Mock(json=lambda: {
                "assets": {"items": [sample_asset_data] * 1000, "total": 1000}
            }),
            # Page 2: full page
            Mock(json=lambda: {
                "assets": {"items": [sample_asset_data] * 1000, "total": 1000}
            }),
            # Page 3: partial page (indicates end)
            Mock(json=lambda: {
                "assets": {"items": [sample_asset_data] * 500, "total": 500}
            }),
        ]
        mock_request.side_effect = responses
        
        assets = mock_client.get_all_assets()
        
        # Should fetch all 2500 assets, not stop at 1000
        assert len(assets) == 2500
        assert mock_request.call_count == 3


def test_get_all_assets_with_limit(mock_client, sample_asset_data):
    """Test fetching assets with a limit."""
    with patch.object(mock_client, '_make_request') as mock_request:
        mock_response = Mock()
        mock_response.json.return_value = {
            "assets": {"items": [sample_asset_data] * 1000}
        }
        mock_request.return_value = mock_response
        
        assets = mock_client.get_all_assets(limit=100)
        
        # Should return only 100 even though API returned 1000
        assert len(assets) == 100


def test_get_all_assets_with_pattern(mock_client):
    """Test filtering assets by filename pattern."""
    with patch.object(mock_client, '_make_request') as mock_request:
        # Create assets with different filenames
        assets_data = [
            {**{"id": f"asset-{i}", "originalFileName": f"IMG_{i}.jpg", 
                "type": "IMAGE", "createdAt": "2024-01-01T12:00:00Z",
                "isFavorite": False, "isArchived": False, "isTrashed": False}}
            for i in range(1, 11)
        ]
        assets_data.extend([
            {**{"id": f"video-{i}", "originalFileName": f"VID_{i}.mp4",
                "type": "VIDEO", "createdAt": "2024-01-01T12:00:00Z",
                "isFavorite": False, "isArchived": False, "isTrashed": False}}
            for i in range(1, 6)
        ])
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "assets": {"items": assets_data}
        }
        mock_request.return_value = mock_response
        
        # Filter only .jpg files
        assets = mock_client.get_all_assets(pattern=r"\.jpg$")
        
        assert len(assets) == 10
        assert all(asset.original_file_name.endswith('.jpg') for asset in assets)


def test_get_all_assets_without_exif(mock_client, sample_asset_data):
    """Test fetching assets without EXIF data."""
    with patch.object(mock_client, '_make_request') as mock_request:
        mock_response = Mock()
        mock_response.json.return_value = {
            "assets": {"items": [sample_asset_data]}
        }
        mock_request.return_value = mock_response
        
        assets = mock_client.get_all_assets(with_exif=False)
        
        # Verify withExif is False
        call_args = mock_request.call_args
        assert call_args[1]['json']['withExif'] is False


def test_get_all_assets_empty_library(mock_client):
    """Test fetching from empty library."""
    with patch.object(mock_client, '_make_request') as mock_request:
        mock_response = Mock()
        mock_response.json.return_value = {
            "assets": {"items": []}
        }
        mock_request.return_value = mock_response
        
        assets = mock_client.get_all_assets()
        
        assert len(assets) == 0
        assert mock_request.call_count == 1


def test_delete_assets(mock_client):
    """Test deleting multiple assets."""
    with patch.object(mock_client, '_make_request') as mock_request:
        mock_request.return_value = Mock()
        
        asset_ids = ["id1", "id2", "id3"]
        mock_client.delete_assets(asset_ids, force=True)
        
        # Verify correct API call
        assert mock_request.call_count == 1
        call_args = mock_request.call_args
        assert call_args[0][0] == "DELETE"
        assert call_args[0][1] == "/assets"
        assert call_args[1]['json']['ids'] == asset_ids
        assert call_args[1]['json']['force'] is True


def test_get_duplicates(mock_client):
    """Test fetching duplicate groups."""
    with patch.object(mock_client, '_make_request') as mock_request:
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "id": "group-1",
                "assets": [
                    {
                        "id": "asset-1",
                        "deviceAssetId": "dev-1",
                        "deviceId": "device-1",
                        "originalPath": "/path1.jpg",
                        "originalFileName": "photo.jpg",
                        "type": "IMAGE",
                        "createdAt": "2024-01-01T12:00:00Z",
                    },
                ],
            }
        ]
        mock_request.return_value = mock_response
        
        groups = mock_client.get_duplicates()
        
        assert len(groups) == 1
        assert groups[0].id == "group-1"


def test_context_manager(mock_client):
    """Test client can be used as context manager."""
    with patch.object(mock_client, 'close') as mock_close:
        with mock_client as client:
            assert client == mock_client
        
        # Verify close was called
        mock_close.assert_called_once()
